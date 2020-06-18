""" Routines to run after a record (or a set of records) is already in place
"""

from pony.orm import db_session


@db_session
def remove_uploaded_records(db, global_config):
    """
    Removes all records archived and uploaded.
    :param db: DB Connection to Pony
    :param global_config: Global Configuration Dict
    :return: 0 on success or -1 on error
    """
    pass


@db_session
def remove_uploaded_archives(db, global_config):
    """

    :param db: DB Connection to Pony
    :param global_config: Global Configuration Dict
    :return: 0 on success or -1 on error
    """
    pass


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
