""" Main file with routines to run Listener
"""

import asyncio
import random
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
    post_recording.remove_uploaded_records(db)
    post_recording.remove_uploaded_archives(db)
    exit(0)


async def processing():

    # Archive, Upload & Remove Records & Archives
    post_recording.archive_records(db, GLOBAL_CONFIG)

    # Uploading check
    up_arch = post_recording.upload_archive(db, AWS_CONFIG)
    up_count = 0
    while up_arch is False and up_count <= 10:
        wait_time = random.randint(10, 90)
        await asyncio.sleep(wait_time)
        up_arch = post_recording.upload_archive(db, AWS_CONFIG)
        up_count += 1
    if up_count > 10:
        exit(-1)

    post_recording.remove_uploaded_archives(db)
    post_recording.remove_uploaded_records(db)


async def main():

    main_logger = logger.get_logger("runner", GLOBAL_CONFIG['log_file'])

    while True:
        if pre_recording.check_aws_budget(db, AWS_CONFIG) < 0:
            main_logger.error(
                " -- AWS Budget {} exceeded -- ".format(
                    AWS_CONFIG['budget_cost']))
            exit(-1)

        perform_cleanup_routines = False

        if pre_recording.check_fs_usage(db, GLOBAL_CONFIG) < 0:
            main_logger.warning(
                " -- FS Usage Check, Exceeded {}MB -- ".format(
                    GLOBAL_CONFIG['storage_usage']))
            perform_cleanup_routines = True

        if pre_recording.check_record_count(db, GLOBAL_CONFIG) < 0:
            main_logger.warning(
                " -- Record Count Check, Exceeded {} --".format(
                    GLOBAL_CONFIG['records_count']))
            perform_cleanup_routines = True

        if perform_cleanup_routines:
            main_logger.info(
                " -- Starting Routines to CleanUP and Uploading --"
            )
            await processing()
        else:
            record_obj = audio.start_recording(db, GLOBAL_CONFIG)
            main_logger.info(
                " -- Record {} Finished -- ".format(record_obj.path)
            )


if __name__ == '__main__':
    signal(SIGINT, exit_handler)
    asyncio.run(main())
