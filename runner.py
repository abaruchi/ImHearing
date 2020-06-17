""" Main file with routines to run Listener
"""


from ImHearing import reader
from ImHearing import logger

GLOBAL_CONFIG = reader.global_config()
AWS_CONFIG = reader.aws_config()
DB_CONFIG = reader.db_config()


def main():

    my_logger = logger.get_logger(__name__, GLOBAL_CONFIG['log_file'])
    my_logger.info('A Info Message')


if __name__ == '__main__':
    main()


