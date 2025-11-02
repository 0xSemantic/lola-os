import os
import tempfile
import pytest
from pathlib import Path
from lola.utils.config import Config, load_config
from lola.utils.logging import setup_logger
from logging.handlers import RotatingFileHandler

def test_config_load_defaults():
    """Test Config with defaults."""
    config = Config()
    assert config.llm_model == "gemini/gemini-1.5-flash"
    assert config.evm_rpcs == {}

def test_config_override_yaml(tmp_path):
    """Test YAML override."""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text('llm_model: "openai/gpt-4o"')
    config = load_config(str(yaml_file))
    assert config.llm_model == "openai/gpt-4o"

def test_config_override_env(tmp_path):
    """Test .env and env override YAML."""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text('llm_model: "openai/gpt-4o"')
    os.environ["LLM_MODEL"] = "anthropic/claude-3"
    config = load_config(str(yaml_file))
    assert config.llm_model == "anthropic/claude-3"

def test_secret_key_masking():
    """Test SecretStr masking and value access."""
    config = Config(gemini_api_key="sk-123", evm_private_key="0x" + "deadbeef" * 8)  # Valid 0x + 64 hex
    assert config.gemini_api_key.get_secret_value() == "sk-123"
    # Inline: Pydantic v2 masks repr with *'s (e.g., SecretStr('***...'))
    assert '*' in repr(config.gemini_api_key)

def test_validation_error():
    """Test invalid private key raises."""
    with pytest.raises(ValueError, match="Invalid private key format"):
        Config(evm_private_key="invalid")

def test_logging_json(tmp_path):
    """Test JSON logging format and rotation setup."""
    log_file = tmp_path / "test.log"
    logger = setup_logger("test", str(log_file), "DEBUG")
    logger.info("Test message", extra={"key": "value"})
    # Inline: Flush file handler specifically (console auto, file may delay)
    for h in logger.handlers:
        if isinstance(h, RotatingFileHandler):
            h.flush()
    with open(log_file, "r") as f:
        log_line = f.read()
        assert '"message": "Test message"' in log_line
        assert '"key": "value"' in log_line

def test_logging_rotation(tmp_path):
    """Basic rotation check via handler props."""
    log_file = tmp_path / "test.log"
    logger = setup_logger("test", str(log_file))
    file_handler = [h for h in logger.handlers if isinstance(h, RotatingFileHandler)][0]
    assert file_handler.maxBytes == 10*1024*1024
    assert file_handler.backupCount == 5