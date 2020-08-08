""" This file contains routines to query Objects into SQLite using Pony
"""

from maya import parse
from pony.orm import db_session, select


@db_session
def get_recorded_entries(db):
    """
    Return all record entries recorded and without an archive associated.
    :param db: db connection
    :return: list with record objects not archived yet
    """
    return select(
        il for il in db.Record if il.status == 'recorded'
    )


@db_session
def get_records_from_archive(archive, db):
    """
    Get a list of records objects inside a given archive object.
    :param archive: an archive object
    :param db: db connection
    :return: list of all record objects associated to an archive
    """
    return select(
        il for il in db.Record if il.archive == archive
    )


@db_session
def get_records_uploaded(db):
    """
    Get a list of records already uploaded to the Object Store.
    :param db: db connection
    :return: list of all records not uploaded
    """
    return select(
        il for il in db.Record if il.archive.uploaded is True
    )


@db_session
def get_archives_uploaded(db):
    """
    Get a list of archives already uploaded to the Object Store.
    :param db: db connection
    :return: list of all archives uploaded
    """
    return select(
        il for il in db.Archive if il.uploaded is True
    )


@db_session
def get_archives_not_uploaded(db):
    """
    Get a list of archives NOT uploaded to the Object Store
    :param db: db connection
    :return: list of all archives NOT uploaded
    """
    return select(
        il for il in db.Archive if il.uploaded is False
    )


@db_session
def get_local_archive_files(db):
    """
    Get all Archives still in local filesystem
    :param db: db connection
    :return: list of all Archives in local filesystem
    """
    return select(
        il for il in db.Archive if il.removed is False
    )


@db_session
def get_local_record_files(db):
    """
    Get all Records still in local filesystem
    :param db: db connection
    :return: list of all Records in local filesystem
    """
    return select(
        il for il in db.Record if il.removed is False
    )


# Views used by Flask / API
@db_session
def get_record_by_date(db, start_datetime=None,
                       end_datetime=None, timez='America/Sao_Paulo'):
    """
    This routine returns all records or archives that has records performed in
    a time range.
    :param start_datetime: Format YYYY-MM-DD HH:MM, where HH:MM is optional
    :param end_datetime: Format YYYY-MM-DD HH:MM, where HH:MM is optional
    :param timez: The timezone used to the query. Default is SAO_PAULO, Brazil
    :param db: DB Connection
    :return: A dict with the Record_ID and the Path (Local or Remote) where you
            can find the record
    """
    ret_dict = dict()
    if start_datetime is None and end_datetime is None:
        return ret_dict

    td_query_start = parse(start_datetime, timezone=timez).datetime(
        to_timezone=timez, naive=False) if start_datetime is not None \
        else start_datetime
    td_query_end = parse(end_datetime, timezone=timez).datetime(
        to_timezone=timez, naive=False) if end_datetime is not None \
        else end_datetime

    if td_query_start and td_query_end is None:
        records_list = select(
            il for il in db.Record if il.start >= td_query_start
        )
    elif td_query_end and td_query_start is None:
        records_list = select(
            il for il in db.Record if il.start <= td_query_end
        )
    else:
        records_list = select(
            il for il in db.Record if
            (il.start >= td_query_start and il.start <= td_query_end) or
            (il.end >= td_query_start and il.start <= td_query_start)
        )

    if len(records_list) == 0:
        return ret_dict

    for rec in records_list:
        if rec.status == 'archived':
            ret_dict[str(rec.id)] = {
                'Archive': rec.archive.remote_path if rec.archive.uploaded
                else rec.archive.local_path,
                'Start': str(rec.start),
                'End': str(rec.end)
            }
        else:
            ret_dict[str(rec.id)] = {
                'Path': rec.path,
                'Start': str(rec.start),
                'End': str(rec.end)
            }
    return ret_dict


@db_session
def get_all_records(db):
    """
    List all records, no filters applied
    :param db: DB Connection
    :return: List of all records
    """
    return list(select(
        records for records in db.Record
    ))


@db_session
def get_all_archives(db):
    """
    List all archives, no filters applied
    :param db: DB Connection
    :return: List of all archives
    """
    return list(select(
        archives for archives in db.Archive
    ))


@db_session
def get_single_record(db, record_id):
    """
    Get a single record, using primary key
    :param db: DB Connection
    :param record_id: record id to return (must be uuid in bytes)
    :return: Record Object
    """
    return db.Record.get(id=record_id)


@db_session
def get_single_archive(db, archive_id):
    """
    Get a single archive, using primary key
    :param db: DB Connection
    :param archive_id: archive id to return (must be uuid in bytes)
    :return: Archive Object
    """
    return db.Archive.get(id=archive_id)
