""" Routines to run after a record (or a set of records) is already in place
"""

import zipfile
from datetime import datetime
from os import path, remove, stat
from uuid import uuid4

import aioboto3
from boto3 import resource
from botocore.exceptions import ConnectionError, EndpointConnectionError
from pony.orm import db_session

from ImHearing.database import query


@db_session
def remove_uploaded_records(db):
    """
    Removes all records archived and uploaded.
    :param db: DB Connection to Pony
    :return: List of Records removed
    """

    list_of_local_records = query.get_local_record_files(db)

    if len(list_of_local_records) == 0:
        return 0

    removed_records_list = list()
    for record in list_of_local_records:
        record_path = record.path

        if not record.removed and path.isfile(record_path):
            remove(record_path)
            record.removed = True
            removed_records_list.append(record)

    return removed_records_list


@db_session
def remove_uploaded_archives(db):
    """
    Remove all archives not uploaded yet.
    :param db: DB Connection to Pony
    :return: List of removed Archives
    """

    list_of_local_archives = query.get_local_archive_files(db)

    if len(list_of_local_archives) == 0:
        return 0

    removed_archives_list = list()
    for archive in list_of_local_archives:
        archive_path = archive.local_path

        if not archive.removed and path.isfile(archive_path):
            remove(archive_path)
            archive.removed = True
            removed_archives_list.append(archive)

    return removed_archives_list


@db_session
def archive_records(db, global_config):
    """
    Adds record(s) to a ZIP Archive to upload to Amazon S3.
    :param db: DB Connection to Pony
    :param global_config: Global Configuration Dict
    :return: Archive Object or False on Error
    """

    list_records_to_archive = query.get_recorded_entries(db)

    if len(list_records_to_archive) == 0 or \
            not path.isdir(global_config['archive_path']):
        return False

    archive_file = global_config['archive_path'] + \
                   str(uuid4()) + '_' + \
                   str(int(datetime.now().timestamp())) + '.zip'

    archive_new = db.Archive(
        creation=datetime.now(),
        local_path=archive_file
    )
    with zipfile.ZipFile(archive_file, 'w') as zip_archive:
        for record in list_records_to_archive:
            zip_archive.write(record.path)
            record.status = 'archived'
            record.archive = archive_new
        archive_new.size = stat(archive_file).st_size / (1024 * 1024)

    return archive_new


@db_session
async def upload_archive(db, aws_config):
    """
    Routine to Upload Archive(s) to AWS S3
    :param aws_config: AWS Config Dict
    :param db: DB Connection to Pony
    :return: List of Archives Uploaded
    """

    archives_to_upload = query.get_archives_not_uploaded(db)

    if len(archives_to_upload) == 0:
        return True

    for archive in archives_to_upload:
        async with aioboto3.resource("s3") as s3:
            file_obj = open(archive.local_path, "rb")
            try:
                await s3.upload_fileobj(
                    file_obj,
                    aws_config['s3_bucket_name'],
                    str(archive.id)
                )
            except (ConnectionError, EndpointConnectionError) as e:
                archive.uploaded = False
                archive.remote_path = ''
                return False
    return True
