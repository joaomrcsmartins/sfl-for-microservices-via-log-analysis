import logging
import os


def config_logging(execution_id: str) -> None:
    """Configure logging. Set up log directory if it does not exist.
    Sets up a file handler to store the logs in a file.
    Configures formats and makes logging properly configured.
    To log import module 'logging' and use the log available.
    E.g.: 'logging.info("This is a info log")'

    Args:
        execution_id (str): id of the execution to be logged in a specific file
    """
    logs_dir = os.path.join(os.getcwd(), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    filename = execution_id + '.log'
    file_handler = logging.FileHandler(
        filename=os.path.join(logs_dir, filename))
    logging.basicConfig(format='%(asctime)s :: %(levelname)s :: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG, handlers=[file_handler])
