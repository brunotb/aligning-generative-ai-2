"""Unit tests for config module."""

from voice_api import config


class TestLogging:
    """Test logging configuration."""

    def test_logger_exists(self):
        """Logger should be configured."""
        assert config.LOGGER is not None

    def test_logger_name(self):
        """Logger should have correct name."""
        assert config.LOGGER.name == "voice_api"

    def test_log_level_set(self):
        """Logger should have a log level set."""
        assert config.LOGGER.level is not None


class TestModelConfiguration:
    """Test model configuration."""

    def test_model_name_set(self):
        """Model name should be configured."""
        assert config.MODEL_NAME is not None
        assert isinstance(config.MODEL_NAME, str)
        assert "gemini" in config.MODEL_NAME.lower()


class TestAudioConfig:
    """Test audio configuration."""

    def test_default_audio_config_creation(self):
        """Should be able to create default audio config."""
        audio_cfg = config.default_audio_config()
        assert audio_cfg is not None

    def test_audio_config_has_sample_rates(self):
        """Audio config should have sample rates."""
        audio_cfg = config.default_audio_config()
        assert audio_cfg.send_sample_rate == 16000
        assert audio_cfg.receive_sample_rate == 24000

    def test_audio_config_has_chunk_size(self):
        """Audio config should have chunk size."""
        audio_cfg = config.default_audio_config()
        assert audio_cfg.chunk_size == 1024

    def test_audio_config_has_channels(self):
        """Audio config should have channel count."""
        audio_cfg = config.default_audio_config()
        assert audio_cfg.channels == 1

    def test_audio_config_frozen(self):
        """AudioConfig should be immutable."""
        audio_cfg = config.default_audio_config()
        try:
            audio_cfg.chunk_size = 2048
            assert False, "Should not be able to modify frozen config"
        except (AttributeError, TypeError):
            pass  # Expected
