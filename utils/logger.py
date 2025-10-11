"""
Centralized logging configuration using Python's logging module.
Provides consistent formatting across all modules.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from rich.logging import RichHandler


def setup_logger(
    name: str,
    level: str = "INFO",
    log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Create a configured logger instance.
    
    Args:
        name: Logger name (typically __name__ from calling module)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for file logging
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler with Rich formatting
    console_handler = RichHandler(
        rich_tracebacks=True,
        markup=True,
        show_time=True,
        show_path=True
    )
    console_handler.setLevel(getattr(logging, level.upper()))
    
    # Format
    formatter = logging.Formatter(
        "%(message)s",
        datefmt="[%X]"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Optional file handler
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


if __name__ == "__main__":
    # Example usage
    test_logger = setup_logger("test_module", level="DEBUG")
    test_logger.debug("This is a debug message")
    test_logger.info("This is an info message")
    test_logger.warning("This is a warning")
    test_logger.error("This is an error")