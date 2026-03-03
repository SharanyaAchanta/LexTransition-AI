import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """
    Creates and returns a configured logger instance.

    Args:
        name (str): The name of the logger (typically __name__).

    Returns:
        logging.Logger: The configured logger instance.
    """
    logger = logging.getLogger(name)

    # Only configure if the logger doesn't already have handlers
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        # Create console handler with standard formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        # Define formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(console_handler)

        # Prevent propagation to the root logger to avoid double logging
        logger.propagate = False

    return logger
