import sys
import logging
import logging.handlers


def set_up_logger(debug: bool = True, log_filename: str = None):
    """
    Sets up the logging module
    """
    level = logging.DEBUG if debug else logging.INFO
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S"
    )

    logger = logging.getLogger()
    logger.setLevel(level)

    if log_filename:
        handler = logging.FileHandler(filename=log_filename)
        handler.setLevel(level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logging.debug("Set up logger")
