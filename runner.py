""" Main file with routines to run Listener
"""

from signal import SIGINT, signal

from pony.orm.dbapiprovider import DatabaseError

from ImHearing import audio, logger, reader
from ImHearing.database import models

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


def exit_handler(signal_received, frame):
    """
    We need to keep the DB consistent in case of a CTRL+C. Also, we perform the
    upload of remaining archives and a cleanup.
    """
    my_logger = logger.get_logger("exit_handler", GLOBAL_CONFIG['log_file'])
    my_logger.info("Terminating - Reveived Signal {}".format(signal_received))

    # --> Archive Routine Here
    # --> Clean Up Routine Here
    exit(0)


def main():

    # 1: Check if all conditions to record is set
    #  1.1: Check Budget (if true stop the process)
    #  1.1: Check file system usage OR number of records (archive and send to
    #                                                      AWS)
    # 2. Start recording

    ## Testing
    for i in range(0, 3):
        audio.start_recording(db, GLOBAL_CONFIG)


if __name__ == '__main__':
    signal(SIGINT, exit_handler)
    main()
