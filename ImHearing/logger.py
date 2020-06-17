""" File with routines to implements Logging
"""

import logging
import sys
from logging.handlers import TimedRotatingFileHandler

FORMATTER = logging.Formatter(
    "%(asctime)s — %(name)s — %(levelname)s — %(message)s")


def get_file_handler(log_file):
    """
    Sets a file handler to a given file
    :param log_file: Path to be used as log
    :return:
    """
    file_handler = TimedRotatingFileHandler(log_file, when='midnight')
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name, log_file):
    """
    Gets a logger to be used to a specific part of the system
    :param logger_name: The name of the looger
    :param log_file: The path to the log file
    :return:
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_file_handler(log_file))

    logger.propagate = False
    return logger
