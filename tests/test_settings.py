from logging import DEBUG

from dotenv import load_dotenv

from template_python.loggers import get_logger
from template_python.settings import Settings

logger = get_logger(__name__)


def test_settings(caplog):
    """
    Test the get_logger function to ensure it returns a logger instance
    and prints a debug message correctly.
    """
    logger.info("[TEST] Running test_settings")
    with caplog.at_level(DEBUG):
        assert load_dotenv(
            dotenv_path=".env.template",
            verbose=True,
        ), "Failed to load environment variables from .env.template"
        settings = Settings()
        assert settings.project_name == "template-python", "Default project name should be 'template-python'"
        logger.debug(f"Settings initialized: {settings}")
