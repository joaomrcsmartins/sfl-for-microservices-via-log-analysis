import logging
import os
import sys

logger: logging.Logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def clean_handlers() -> None:
    """Remove the handlers attached to the logger. Useful when running multiple scenarios in a row.
    """
    logger.handlers.clear()


def config_logger(
    execution_id: str
) -> None:
    """Configure the application logger.
    Sets up log directory if it does not exist.
    Sets up a file handler to store the logs in a file and stream handler for the console/terminal.
    To log import the logger from this module
    E.g.: 'from sfldebug.tools.logger import logger'

    Args:
        execution_id (str): id of the execution to be logged in a specific file
    """
    logs_dir = os.path.join(os.getcwd(), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    filename = execution_id + '.log'
    file_handler = logging.FileHandler(
        filename=os.path.join(logs_dir, filename))
    console_handler = logging.StreamHandler(sys.stdout)

    log_formatter = logging.Formatter(
        fmt='%(asctime)s :: %(levelname)s :: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_formatter)

    # Add logger console handler if not already added
    has_console_handler = False
    for handler in logger.handlers:
        has_console_handler |= isinstance(handler, logging.StreamHandler)
    if not has_console_handler:
        logger.addHandler(console_handler)

    logger.addHandler(file_handler)
