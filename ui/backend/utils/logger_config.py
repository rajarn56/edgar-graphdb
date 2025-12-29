"""Logging configuration for UI backend"""

import os
import sys
from pathlib import Path
from datetime import datetime
from loguru import logger
from typing import Optional


def setup_logger(
    app_name: str = "ui_backend",
    log_level: Optional[str] = None,
    log_dir: Optional[str] = None,
    console_output: bool = True
) -> None:
    """
    Configure loguru logger with file and console handlers.
    
    Args:
        app_name: Name of the application (default: 'ui_backend')
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR). Defaults to LOG_LEVEL env var or INFO
        log_dir: Directory for log files. Defaults to LOG_DIR env var or 'logs'
        console_output: Whether to output logs to console. Default: True
    """
    # Remove default handler
    logger.remove()
    
    # Get configuration from environment or defaults
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    if log_dir is None:
        log_dir = os.getenv("LOG_DIR", "logs")
    
    # Ensure log directory exists
    log_path = Path(__file__).parent.parent / log_dir
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Create log file name with date
    date_str = datetime.now().strftime("%Y%m%d")
    log_file = log_path / f"{app_name}_{date_str}.log"
    error_log_file = log_path / f"errors_{date_str}.log"
    access_log_file = log_path / f"access_{date_str}.log"
    
    # Format for structured logging
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # Add file handler for all logs
    logger.add(
        log_file,
        format=log_format,
        level=log_level,
        rotation="100 MB",  # Rotate when file reaches 100MB
        retention="30 days",  # Keep logs for 30 days
        compression="zip",  # Compress old logs
        encoding="utf-8",
        enqueue=True,  # Thread-safe logging
    )
    
    # Add separate error log file
    logger.add(
        error_log_file,
        format=log_format,
        level="ERROR",
        rotation="100 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8",
        enqueue=True,
    )
    
    # Add access log file for HTTP requests
    access_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{message}"
    )
    logger.add(
        access_log_file,
        format=access_format,
        level="INFO",
        filter=lambda record: "access" in record["extra"],
        rotation="100 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8",
        enqueue=True,
    )
    
    # Add console handler if requested
    if console_output:
        # Simpler format for console
        console_format = (
            "<green>{time:HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<level>{message}</level>"
        )
        logger.add(
            sys.stderr,
            format=console_format,
            level=log_level,
            colorize=True,
        )
    
    logger.info(f"Logger configured: {app_name}")
    logger.info(f"Log file: {log_file}")
    logger.info(f"Error log file: {error_log_file}")
    logger.info(f"Access log file: {access_log_file}")
    logger.info(f"Log level: {log_level}")


def get_logger(name: Optional[str] = None):
    """
    Get a logger instance.
    
    Args:
        name: Optional logger name (for module-specific logging)
    
    Returns:
        Logger instance
    """
    if name:
        return logger.bind(name=name)
    return logger

