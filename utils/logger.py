"""
Logging module for VB6 Project Mapper
Provides consistent logging across all modules with different log levels
"""

import os
import sys
import json
import uuid
import logging
import logging.config
from datetime import datetime

# Generate a unique run ID
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + str(uuid.uuid4())[:8]


def setup_logging(name=None, console_level=None, config_file="logging_config.json"):
    """
    Set up logging using configuration file with optional overrides

    Args:
        name (str, optional): Logger name, typically __name__ from the calling module
        console_level (int, optional): Override console log level from command line
        config_file (str, optional): Path to logging configuration file

    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger instance
    logger_name = name or "vb6mapper"
    logger = logging.getLogger(logger_name)

    # Only configure if it hasn't been done already
    if not logging.getLogger().handlers:
        # Ensure log directories exist
        create_log_directories()

        # Load configuration
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)

            # Update filenames with timestamp
            for handler in config["handlers"].values():
                if "filename" in handler:
                    handler["filename"] = handler["filename"].replace("TIMESTAMP", RUN_ID)

            # Apply configuration
            logging.config.dictConfig(config)

            # Log initialization
            root_logger = logging.getLogger()
            root_logger.info(f"Logging initialized with Run ID: {RUN_ID}")
        else:
            # Fallback to basic configuration if config file is missing
            logging.basicConfig(
                level=logging.INFO,
                format="%(levelname)s: %(message)s",
                stream=sys.stderr
            )
            logger.warning(f"Config file {config_file} not found, using basic configuration")

    # Override console handler level if specified (e.g., from command line)
    if console_level is not None:
        for handler in logging.getLogger().handlers:
            if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stderr:
                handler.setLevel(console_level)
                logger.debug(f"Console log level overridden to: {console_level}")

    return logger


def create_log_directories():
    """Create the directory structure for log files"""
    log_dirs = [
        "logs/debug",
        "logs/info",
        "logs/warning",
        "logs/error",
        "logs/critical"
    ]

    for directory in log_dirs:
        os.makedirs(directory, exist_ok=True)


def get_logger(name=None):
    """
    Get an existing logger or create a new one

    Args:
        name (str, optional): Logger name, typically __name__ from the calling module

    Returns:
        logging.Logger: Logger instance
    """
    logger_name = name or "vb6mapper"
    return logging.getLogger(logger_name)


def get_run_id():
    """
    Get the unique ID for the current run

    Returns:
        str: The run ID
    """
    return RUN_ID