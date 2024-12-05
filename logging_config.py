import logging
import logging.handlers
from datetime import datetime
from pathlib import Path

from tqdm import tqdm


class TqdmLoggingHandler(logging.Handler):
    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.write(msg)
            self.flush()
        except Exception:
            self.handleError(record)


def setup_logging(app_name: str = "flashscore_scraper") -> None:
    """
    Set up logging configuration with both file and console handlers.

    Args:
        app_name: Name of the application, used for log file naming
    """
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = logs_dir / f"{app_name}_{timestamp}.log"

    # Set logging levels for all loggers except those starting with "browsers", "models", "services" prefixes to WARNING level, to avoid excessive logging
    for logger_name in logging.root.manager.loggerDict:
        if not any(
            logger_name.startswith(prefix)
            for prefix in ["browsers", "models", "services"]
        ):
            logging.getLogger(logger_name).setLevel(logging.WARNING)

    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Capture all levels

    # Remove any existing handlers
    root_logger.handlers = []

    # Create formatters
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_formatter = logging.Formatter("%(levelname)s - %(message)s")

    # File handler - log everything to file
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"  # 10MB
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # Console handler - only log warnings and above
    # console_handler = logging.StreamHandler()
    console_handler = TqdmLoggingHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # Log the start of a new session
    root_logger.info(f"=== Starting new logging session for {app_name} ===")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Name for the logger, typically __name__ of the module

    Returns:
        Logger instance configured with the application's settings
    """
    return logging.getLogger(name)
