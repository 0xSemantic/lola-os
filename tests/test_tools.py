# Standard imports
import pytest
import asyncio
from unittest.mock import patch, Mock, MagicMock

# Third-party imports
# None unique (pytest from dev)

# Local imports
from lola.tools.base import BaseTool
from lola.tools.web_crawl import WebCrawlTool
from lola.tools.onchain.contract_call import ContractCallTool
from lola.tools.onchain.transact import TransactTool
from lola.tools.onchain.utils import gas_helper, simulate_tx
from lola.utils.config import load_config

"""
File: Unit and integration tests for LOLA tools (base/web_crawl/onchain).

Purpose: Validates base execute/validate/bind, web crawl async/extract, onchain call/transact/sim, with real/mocked crawl/EVM.
How: pytest for unit (mocks for async/broadcast), integration (config-driven real where possible), edges (retry on fail, revert abort).
Why: Ensures reliable tools in Phase 5, with >80% coverage for market-ready bind/execute.
Full Path: lola-os/tests/test_tools.py
"""

def test_base_tool_validate_bind():
    """Test BaseTool validate/bind to mock agent.

    Does Not: Test execute—abstract.
    """
    class MockTool(BaseTool):
        def execute(self, **kwargs):
            return "Mock result"

    tool = MockTool("mock_tool", "Mock tool description")
    assert tool.validate(url="test")["valid"] == True  # Basic str check
    with pytest.raises(ValueError):
        tool.validate(url="")  # Empty fails
    mock_agent = Mock(tools=[])
    tool.bind_to_agent(mock_agent)
    assert len(mock_agent.tools) == 1


@pytest.mark.asyncio
@patch('lola.tools.web_crawl.AsyncWebCrawler.arun')
def test_web_crawl_execute(mock_arun):
    """Test WebCrawlTool async execute with mock crawler.

    Args:
        mock_arun: Patched arun.

    Does Not: Test retries—mock success.
    """
    mock_result = Mock()
    mock_result.json = "Test JSON content"
    mock_result.markdown = "Test MD"
    mock_result.page_title = "Test"
    mock_result.links = ["link"]
    mock_arun.return_value = mock_result
    tool = WebCrawlTool()
    result = asyncio.run(tool.execute(url="https://example.com"))
    assert "Test JSON content" in result["content"]
    assert result["metadata"]["title"] == "Test"
    mock_arun.assert_called_once()


@patch('lola.chains.contract.LOLAContract.call')
def test_contract_call_tool(mock_call):
    """Test ContractCallTool execute with mock contract call.

    Args:
        mock_call: Patched call.

    Does Not: Test ABI load—str ABI.
    """
    mock_call.return_value = 1000
    tool = ContractCallTool()
    result = tool.execute(address="0xaddr", abi='[{"name": "balanceOf", "inputs": [{"type": "address"}], "outputs": [{"type": "uint256"}]}]', function_name="balanceOf", "0xuser")
    assert result == 1000
    mock_call.assert_called_once()


@patch('lola.chains.wallet.LOLAWallet.sign_tx')
@patch('lola.chains.connection.Web3Connection.w3.eth.send_raw_transaction')
def test_transact_tool(mock_broadcast, mock_sign):
    """Test TransactTool execute with mock sign/broadcast.

    Args:
        mock_broadcast: Patched send_raw_transaction.
        mock_sign: Patched sign_tx.

    Does Not: Test sim/gas—assume pre-called.
    """
    mock_sign.return_value = b"signed_tx"
    mock_broadcast.return_value = Mock(hex=Mock(return_value="0xhash"))
    tool = TransactTool()
    result = tool.execute(to="0xto", value=0, data=None, chain="sepolia")
    assert "tx_hash" in result
    assert result["tx_hash"] == "0xhash"
    mock_sign.assert_called_once()
    mock_broadcast.assert_called_once()


def test_onchain_utils_gas_sim():
    """Test gas_helper/simulate_tx with mock connection.

    Does Not: Test real—mock success.
    """
    with patch('lola.chains.connection.Web3Connection') as mock_conn_class:
        mock_conn = Mock()
        mock_w3 = Mock()
        mock_eth = Mock()
        mock_eth.estimate_gas.return_value = 21000
        mock_eth.call.return_value = b"success"
        mock_w3.eth = mock_eth
        mock_conn.w3 = mock_w3
        mock_conn_class.return_value = mock_conn
        tx = {"to": "0xaddr", "value": 0}
        gas = gas_helper("sepolia", tx)
        assert gas == 21000
        sim = simulate_tx("sepolia", tx)
        assert sim == b"success"


# Edge: Web crawl fail retry (mock timeout then success)
@pytest.mark.asyncio
@patch('lola.tools.web_crawl.AsyncWebCrawler.arun')
def test_web_crawl_retry(mock_arun):
    """Test WebCrawlTool retries on fail.

    Args:
        mock_arun: Side-effect timeout then success.

    Does Not: Test selector—default.
    """
    mock_success = Mock()
    mock_success.json = "Success JSON"
    mock_success.page_title = "Test"
    mock_success.links = ["link"]
    mock_arun.side_effect = [Exception("Timeout"), mock_success]
    tool = WebCrawlTool()
    result = asyncio.run(tool.execute(url="url"))
    assert "Success JSON" in result["content"]
    mock_arun.assert_called()


# Edge: Transact sim revert
@patch('lola.chains.wallet.LOLAWallet.sign_tx')
def test_transact_revert(mock_sign):
    """Test TransactTool raises on sim revert.

    Args:
        mock_sign: Patched sign_tx (unused if sim fails).

    Does Not: Test success—revert only.
    """
    with patch('lola.chains.utils.simulate_call') as mock_sim:
        mock_sim.return_value = {"revert": "Insufficient funds"}
        tool = TransactTool()
        with pytest.raises(ValueError, match="TX simulation reverted"):
            tool.execute(to="0xto", value=1000000000000000000, chain="sepolia")
        mock_sim.assert_called()


# Edge: Contract call invalid function
@patch('lola.chains.contract.LOLAContract.call')
def test_contract_call_invalid(mock_call):
    """Test ContractCallTool raises on invalid function.

    Args:
        mock_call: Patched call (raises).

    Does Not: Test ABI—via validate.
    """
    mock_call.side_effect = ValueError("Function not in ABI")
    tool = ContractCallTool()
    with pytest.raises(ValueError, match="Function not in ABI"):
        tool.execute(address="0xaddr", abi='[{"name": "balanceOf", "inputs": [{"type": "address"}], "outputs": [{"type": "uint256"}]}]', function_name="invalid", "0xuser")
    mock_call.assert_called_once()