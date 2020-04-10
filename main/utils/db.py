""""
File with connections routine/classes to Databases and Cloud
"""

import os
import sqlite3
from datetime import datetime


class SQLQueries(object):
    """
    This class builds queries used for several pourpoeses
    """

    def sql_add_archive(self, archive_metadata):
        """
        Builds the SQL necessary to add an archive into Database.
        :param archive_metadata: a dict with metadata to add an archive into DB
        :return: a string with the SQL to be used to add the Archive
        """

        insert_part_01 = r'INSERT INTO ArchiveTable (archive_id, ' \
                         r'archive_creation_date, path, uploaded) VALUES('
        insert_part_02 = r');'

        insert_query = insert_part_01 + '\'' + \
                       str(archive_metadata['archive_id']) + \
                       ', \'' + str(archive_metadata['archive_creation_date']) \
                       + '\', \'' + str(archive_metadata['path']) + \
                       '\', \'False\'' + insert_part_02
        return insert_query

    def sql_add_records_to_archive(self, records_id, archive_id):
        """
        This method builds the SQL to add a set of Records into an Archive
        :param records_id: a LIST of record_id to add
        :param archive_id: a single archive_id
        :return: a List of SQL Queries to add records into an archive
        """

        insert_list = list()
        insert_part_01 = r'INSERT INTO RecordArchiveTable ' \
                         r'(fk_record_id, fk_archive_id) VALUES('
        insert_part_02 = r');'
        archive = str(archive_id)
        for record in records_id:
            insert_query = insert_part_01 + '\'' + str(record) + \
                           ', \'' + archive + '\'' + insert_part_02
            insert_list.append(insert_query)

        return insert_list

    def sql_add_record(self, record_metadata):
        """
        Builds the SQL necessary to add a record into Database
        :param record_metadata: a dict with metadata to add a record into DB
        :return: a dict with queries to be used to add records into DB
        """
        dict_queries = dict()
        current_date = datetime.now()

        insert_part_01 = r'INSERT INTO RecordTable (record_id, record_date, ' \
                         r'record_start, record_end, record_size, ' \
                         r'uploaded, path) '
        insert_part_02 = 'VALUES('
        insert_part_03 = ');'

        for record_id, value in record_metadata.items():
            insert_query = insert_part_01 + insert_part_02 + '\'' + \
                           record_id + '\''+ ',' + '\'' + str(current_date) + \
                           '\'' + ',' + '\'' + str(value['time_start']) + \
                           '\'' + ',' + '\'' + str(value['time_end']) + \
                           '\'' + ',' + '\'' + str(value['file_size']) + \
                           '\'' + ',' + '\'' + str(value['uploaded']) + \
                           '\'' + ',' + '\'' + value['file_path'] + \
                           '\'' + insert_part_03
            dict_queries[record_id] = insert_query

        return dict_queries

    def sql_add_user(self, user_metadata):
        """
        Builds the SQL necessary to add an user into Database
        :param user_metadata: a dict with metadata to add an user into DB
        :return: A dict with the SQL to add a user or several users
        """
        dict_queries = dict()

        insert_part_01 = r'INSERT INTO TableUsers (user_id, user_name, ' \
                        r'user_email, user_pass, last_login) VALUES ('
        insert_part_02 = ');'

        for user_id, value in user_metadata.items():
            insert_query = insert_part_01 + '\'' + user_id + '\', \'' + \
                           str(value['user_name']) + '\', \'' + \
                           str(value['user_email']) + '\', \'' + \
                           str(value['user_pass']) + '\',None \'' + \
                           insert_part_02
            dict_queries[user_id] = insert_query
        return dict_queries

    def sql_add_token(self, token_metadata):
        """
        Builds the SQL necessary to add a token into Database
        :param token_metadata:
        :return:
        """
        pass

    def sql_remove_user(self, user_metadata):
        """
        Builds the SQL necessary to remove a token from Database
        :param user_metadata:
        :return:
        """
        pass


def create_sqlite_db(db_file=None):
    """
    Creates the initial SQLite database

    :param db_file: Path to be used as SQ
    :return:
    """

    if db_file is None:
        sqlite_db_path = 'SQLiteDB/ImHearing.db'
    else:
        sqlite_db_path = db_file

    conn = sqlite3.connect(sqlite_db_path)
    c = conn.cursor()
    sqlitedb_script = 'SQLiteScripts/ImHearing_sqlite_create.sql'

    fd = open(sqlitedb_script, 'r')
    sqlFile = fd.read()

    sql_commands = sqlFile.split(';')
    for command in sql_commands:
        try:
            c.execute(command)
        except sqlite3.OperationalError as msg:
            print("Command skipped: ", msg)

    if os.path.isfile(sqlite_db_path):
        ret_val = (True, sqlite_db_path)
    else:
        ret_val = (False, "DB Not Created")

    return ret_val


def is_archived(record_id):
    """
    Checks if a given record is archive or not.
    :param record_id: the UUID of the record_id to check
    :return: False or the archive_id where the record is stored
    """
    pass


def is_uploaded(unique_id):
    """
    Checks if a given record or archive is already uploaded
    :param unique_id: the record or archive UUID to check
    :return: True or False
    """
    pass
