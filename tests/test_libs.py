# Standard imports
import pytest
import asyncio
from unittest.mock import patch, Mock, MagicMock

# Third-party imports
# None unique (pytest from dev)

# Local imports
from lola.utils.config import load_config
from lola.libs.langgraph.adapter import SupervisedStateGraph
from lola.libs.litellm.proxy import LLMProxy
from lola.libs.crawl4ai.crawler import LOLAWebCrawler
from lola.libs.web3.utils import gas_estimate, simulate_call

"""
File: Unit and integration tests for LOLA libs adapters.

Purpose: Validates full functionality of LangGraph/LiteLLM/Crawl4AI/web3 adapters with real/mocked calls.
How: Uses pytest for unit (mocks), integration (config-driven real where possible), edges (failures/fallbacks).
Why: Ensures market-ready reliability from Phase 2, no mocks in prod but tested here for coverage.
Full Path: lola-os/tests/test_libs.py
"""

# Note: Real Gemini needs key; mock for CI, user real


@patch('lola.libs.litellm.proxy.completion')
@patch('lola.libs.litellm.proxy.model_cost')
def test_litellm_proxy(mock_cost, mock_completion):
    """Test LiteLLM proxy complete with fallback.

    Args:
        mock_completion: Patched litellm.completion (local module).
        mock_cost: Patched model_cost (local module).

    Does Not: Test cost—separate method.
    """
    mock_response = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "Test response"
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    mock_completion.return_value = mock_response
    mock_cost.return_value = 0.0001
    proxy = LLMProxy("gemini/gemini-1.5-flash")
    response = proxy.complete("Test prompt")
    assert "Test response" in response
    mock_completion.assert_called_once()
    mock_cost.assert_called_once()


@patch('lola.libs.litellm.proxy.completion')
@patch('lola.libs.litellm.proxy.model_cost')
def test_litellm_fallback(mock_cost, mock_completion):
    """Test fallback on primary fail.

    Args:
        mock_completion: Side-effect fail then success (local module).
        mock_cost: Patched model_cost (local module).

    Does Not: Test cost in fallback—complete only.
    """
    mock_response = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "Fallback OK"
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    mock_completion.side_effect = [Exception("Fail"), mock_response]
    mock_cost.return_value = 0.0001
    proxy = LLMProxy("fail-model", ["success-model"])
    response = proxy.complete("Prompt")
    assert "Fallback OK" in response
    assert mock_completion.call_count == 2
    mock_cost.assert_called()


def test_langgraph_supervise():
    """Test LangGraph adapter supervision.

    Does Not: Invoke full graph—compile only.
    """
    class MockState: pass
    graph = SupervisedStateGraph(MockState)
    graph.add_turn_limit_node()
    graph.add_reflection_node()
    compiled = graph.compile_supervised()
    assert hasattr(compiled, "invoke")


@patch('crawl4ai.AsyncWebCrawler.arun')
def test_crawl4ai(mock_arun):
    """Test Crawl4AI wrap.

    Args:
        mock_arun: Patched arun.

    Does Not: Test retries—separate edge.
    """
    mock_result = MagicMock()
    mock_result.json = "Test JSON content"
    mock_result.markdown = "Test MD"
    mock_result.page_title = "Test"
    mock_result.links = ["link"]
    mock_arun.return_value = mock_result
    crawler = LOLAWebCrawler()
    result = asyncio.run(crawler.crawl("https://example.com"))
    assert "Test JSON content" in result["content"]
    assert result["metadata"]["title"] == "Test"


@patch('crawl4ai.AsyncWebCrawler.arun')
def test_crawl_retry(mock_arun):
    """Test crawl retries.

    Args:
        mock_arun: Side-effect fail then success.

    Does Not: Test max_retries >2—default 3.
    """
    mock_success = MagicMock()
    mock_success.json = "Success JSON"
    mock_success.page_title = "Test"
    mock_success.links = ["link"]
    mock_arun.side_effect = [Exception("Timeout"), mock_success]
    crawler = LOLAWebCrawler(max_retries=2)
    result = asyncio.run(crawler.crawl("url"))
    assert "Success JSON" in result["content"]
    mock_arun.assert_called()


# def test_web3_connection():
#     """Test Web3Connection multi-RPC.

#     Does Not: Test switch—init only.
#     """
#     # Patch everything inside Web3Connection to avoid real connection attempts
#     with patch('lola.libs.web3.connection.load_config') as mock_load_config:
#         mock_config = Mock()
#         mock_config.evm_rpcs = {"sepolia": "http://mock-rpc"}
#         mock_load_config.return_value = mock_config

#         with patch('web3.providers.HTTPProvider') as mock_provider, \
#              patch('web3.Web3') as MockWeb3, \
#              patch('web3.main.Web3.attach_modules', return_value=None):

#             mock_provider.return_value = Mock()
#             mock_w3 = Mock()
#             mock_w3.is_connected.return_value = True
#             MockWeb3.return_value = mock_w3

#             from lola.libs.web3.connection import Web3Connection
#             conn = Web3Connection("sepolia")

#             # Verify attributes and mocks
#             assert conn.chain == "sepolia"
#             assert conn.rpc_url == "http://mock-rpc"
#             assert conn.w3.is_connected()


# def test_web3_contract():
#     """Test contract call.

#     Does Not: Test ABI load from file—str ABI.
#     """
#     with patch('lola.libs.web3.contract.Web3Connection') as mock_conn_class:
#         # Proper nested mocks
#         mock_conn = Mock()
#         mock_w3 = Mock()
#         mock_eth = Mock()
#         mock_contract = Mock()

#         # Simulate contract function returning 42
#         mock_test_func = Mock()
#         mock_test_func.call = Mock(return_value=42)

#         # Map function name properly
#         mock_contract.functions = {"test": mock_test_func}

#         mock_eth.contract.return_value = mock_contract
#         mock_w3.eth = mock_eth
#         mock_conn.w3 = mock_w3
#         mock_conn_class.return_value = mock_conn

#         from lola.libs.web3.contract import LOLAContract
#         abi = [{"name": "test", "inputs": [], "outputs": [{"type": "uint256"}]}]
#         contract = LOLAContract("0xaddr", abi, mock_conn)
#         result = contract.call("test")

#         assert result == 42
#         mock_eth.contract.assert_called_once()


@patch('lola.libs.web3.wallet.load_config')
@patch('eth_account.Account.from_key')
@patch('lola.libs.web3.wallet.Web3Connection')
def test_web3_wallet(mock_conn_class, mock_account, mock_load_config):
    """Test wallet balance/sign.

    Args:
        mock_load_config: Patched load_config (local module).
        mock_account: Patched from_key.
        mock_conn_class: Patched Web3Connection.

    Does Not: Test sign—balance only.
    """
    with patch('lola.utils.config.load_config') as mock_load_config:
        mock_config = Mock()
        mock_pk = Mock()
        mock_pk.get_secret_value.return_value = "0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
        mock_config.evm_private_key = mock_pk
        mock_load_config.return_value = mock_config
        mock_conn = Mock()
        mock_w3 = Mock()
        mock_eth = Mock()
        mock_eth.get_balance.return_value = 1000000000000000000
        mock_w3.eth = mock_eth
        mock_conn.w3 = mock_w3
        mock_conn_class.return_value = mock_conn
        mock_account.return_value = Mock(address="0xaddr")
        from lola.libs.web3.wallet import LOLAWallet
        wallet = LOLAWallet(connection=mock_conn)
        balance = wallet.balance()
        assert balance == 1000000000000000000
        mock_eth.get_balance.assert_called_once()


def test_web3_utils_gas_sim():
    """Test gas/sim utils (mock provider).

    Does Not: Test error case—success only.
    """
    conn = Mock(w3=Mock(eth=Mock(estimate_gas=Mock(return_value=21000),
                                 call=Mock(return_value=b"success"))))
    tx = {"to": "0xaddr", "value": 0}
    gas = gas_estimate(conn, tx)
    assert gas == 21000
    sim = simulate_call(conn, tx)
    assert sim == b"success"
