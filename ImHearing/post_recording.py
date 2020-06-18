""" Routines to run after a record (or a set of records) is already in place
"""

from os import path, remove

from pony.orm import db_session

from ImHearing import logger
from ImHearing.database import query


@db_session
def remove_uploaded_records(db, global_config):
    """
    Removes all records archived and uploaded.
    :param db: DB Connection to Pony
    :param global_config: Global Configuration Dict
    :return: List of Records removed
    """

    list_of_local_records = query.get_local_record_files(db)
    my_logger = logger.get_logger('ImHearing.post_recording',
                                  global_config['log_file'])

    if len(list_of_local_records) == 0:
        return 0

    removed_records_list = list()
    for record in list_of_local_records:
        record_path = record.path

        if not record.removed and path.isfile(record_path):
            remove(record_path)
            record.removed = True
            my_logger.info(" -- Record {} Removed".format(record.path))
            removed_records_list.append(record)

    return removed_records_list


@db_session
def remove_uploaded_archives(db, global_config):
    """
    Remove all archives not uploaded yet.
    :param db: DB Connection to Pony
    :param global_config: Global Configuration Dict
    :return: List of removed Archives
    """

    list_of_local_archives = query.get_local_archive_files(db)
    my_logger = logger.get_logger('ImHearing.post_recording',
                                  global_config['log_file'])

    if len(list_of_local_archives) == 0:
        return 0

    removed_archives_list = list()
    for archive in list_of_local_archives:
        archive_path = archive.local_path

        if not archive.removed and path.isfile(archive_path):
            remove(archive_path)
            archive.removed = True
            my_logger.info(" -- Archive {} Removed --".format(archive_path))
            removed_archives_list.append(archive)

    return removed_archives_list


@db_session
def archive_records(db, global_config):
    """

    :param db: DB Connection to Pony
    :param global_config: Global Configuration Dict
    :return: 0 on success or -1 on error
    """
    pass


@db_session
def upload_archive(db, global_config):
    """

    :param db: DB Connection to Pony
    :param global_config: Global Configuration Dict
    :return: 0 on success or -1 on error
    """
    pass
