""" Main file with routines to run Listener
"""

from pony.orm.dbapiprovider import DatabaseError

from ImHearing import logger, reader
from ImHearing.database import models, query

# Configurations Sections
GLOBAL_CONFIG, global_ret = reader.global_config()
AWS_CONFIG, aws_ret = reader.aws_config()
DB_CONFIG, db_ret = reader.db_config()

if global_ret < 0 or aws_ret < 0 or db_ret < 0:
    print("-- Some Error Found when Reading Config File --")
    if global_ret < 0:
        print(GLOBAL_CONFIG)
    elif aws_ret < 0:
        print(AWS_CONFIG)
    elif db_ret < 0:
        print(DB_CONFIG)
    exit(-1)

# Defines the DB Connection to Pony
try:
    db = models.define_db(
        provider='sqlite',
        filename=DB_CONFIG['db_path'],
        create_db=True
    )
except DatabaseError as e:
    print("ERROR: {}".format(e))
    print("-- Recreate the DB or Try some DB Recovery Utility --")
    exit(-1)


def main():

    my_logger = logger.get_logger(__name__, GLOBAL_CONFIG['log_file'])
    my_logger.info('A Info Message')


if __name__ == '__main__':
    main()
