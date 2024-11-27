import logging
from rich.logging import RichHandler
import sys

def get_formatted_logger():
    """Return a formatted logger."""
    logger = logging.getLogger("scraper")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # Rich handler for console output
        console_handler = RichHandler(
            rich_tracebacks=True,
            show_time=True,
            show_path=False,
            markup=True
        )
        console_handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(console_handler)

        # HTTP handler remains the same
        from logging.handlers import HTTPHandler
        http_handler = HTTPHandler(
            'localhost:8700',
            '/log',
            method='POST',
        )
        http_formatter = logging.Formatter(
            "%(levelname)s [%(asctime)s] %(message)s",
            datefmt="%H:%M:%S"
        )
        http_handler.setFormatter(http_formatter)
        logger.addHandler(http_handler)

    logger.propagate = False
    return logger
