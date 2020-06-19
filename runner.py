""" Main file with routines to run Listener
"""

from signal import SIGINT, signal

from pony.orm.dbapiprovider import DatabaseError

from ImHearing import audio, logger, post_recording, pre_recording, reader
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

    # Archive
    post_recording.archive_records(db, GLOBAL_CONFIG)

    # --> Clean Up Routine Here
    post_recording.remove_uploaded_records(db, GLOBAL_CONFIG)
    post_recording.remove_uploaded_archives(db, GLOBAL_CONFIG)
    exit(0)


def main():

    main_logger = logger.get_logger("runner", GLOBAL_CONFIG['log_file'])

    if pre_recording.check_aws_budget(db, AWS_CONFIG) < 0:
        main_logger.error(
            " -- AWS Budget {} exceeded -- ".format(AWS_CONFIG['budget_cost']))
        exit(-1)

    while True:
        perform_cleanup_routines = False
        if pre_recording.check_fs_usage(db, GLOBAL_CONFIG) < 0:
            main_logger.error(
                " -- FS Usage Check, Exceeded {}% -- ".format(
                    GLOBAL_CONFIG['storage_usage']))
            perform_cleanup_routines = True

        if pre_recording.check_record_count(db, GLOBAL_CONFIG) < 0:
            main_logger.error(
                " -- Record Count Check, Exceeded {} --".format(
                    GLOBAL_CONFIG['records_count']))
            perform_cleanup_routines = True

        if perform_cleanup_routines:
            # Archive, Upload & Remove Records & Archives
            post_recording.archive_records(db, GLOBAL_CONFIG)
            post_recording.upload_archive(db, AWS_CONFIG)
            post_recording.remove_uploaded_archives(db)
            post_recording.remove_uploaded_records(db)
            main_logger.info(" -- Archive and Upload routines Finished -- ")
        else:
            record_obj = audio.start_recording(db, GLOBAL_CONFIG)
            main_logger.info(
                " -- Record {} Finished -- ".format(record_obj.path)
            )


if __name__ == '__main__':
    signal(SIGINT, exit_handler)
    main()
