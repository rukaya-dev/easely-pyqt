import logging
import os

dir_path = os.getcwd()
app_file_path = "app.log"


def set_up_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    console_handler = logging.StreamHandler()
    error_file_handler = logging.FileHandler(app_file_path)

    console_handler.setLevel(logging.DEBUG)
    error_file_handler.setLevel(logging.DEBUG)

    console_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console_handler.setFormatter(console_format)
    error_file_handler.setFormatter(file_format)

    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(error_file_handler)

    return logger
