""" Routines to read configuration file - config.ini
"""

import configparser
from os import getcwd, path

config_parser = configparser.ConfigParser()


def global_config(config_file=None):
    """
    Get configuration related to Global Section
    :param config_file: File to be used as config.ini, if None use default
    :return: Dict with all Global Configurations
    """
    if config_file is None:
        config_file = getcwd().replace('ImHearing',
                                       'ImHearing/config.ini')

    if not path.isfile(config_file):
        return 'File {} Not Found'.format(config_file), -1

    config_parser.read(config_file)
    return config_parser['GLOBAL']


def aws_config(config_file=None):
    """
    Get configuration related to AWS Section
    :param config_file: File to be used as config.ini, if None use default
    :return: Dict with all AWS Configurations
    """
    if config_file is None:
        config_file = getcwd().replace('ImHearing',
                                       'ImHearing/config.ini')

    if not path.isfile(config_file):
        return 'File {} Not Found'.format(config_file), -1

    config_parser.read(config_file)
    return config_parser['AWS']


def db_config(config_file=None):
    """
    Get configuration related to Database (SQLite) Section
    :param config_file: File to be used as config.ini, if None use default
    :return: Dict with all DB Configurations
    """
    if config_file is None:
        config_file = getcwd().replace('ImHearing',
                                       'ImHearing/config.ini')

    if not path.isfile(config_file):
        return 'File {} Not Found'.format(config_file), -1

    config_parser.read(config_file)
    return config_parser['CONFIGDB']
