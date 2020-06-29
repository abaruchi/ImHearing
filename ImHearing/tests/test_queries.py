""" Test queries implemented in ImHearing/database/queries.py
"""

import datetime
import unittest
from enum import Enum

import pytz
from pony.orm import db_session

from ImHearing.database.models import define_db
from ImHearing.database.query import (
    get_archives_not_uploaded, get_archives_uploaded, get_local_archive_files, get_local_record_files,
    get_record_by_date, get_recorded_entries, get_records_from_archive, get_records_uploaded)


class RecordStatus(Enum):
    recorded = 1
    archived = 2


class TestQueries(unittest.TestCase):

    def setUp(self):
        self.db_test = define_db(
            provider='sqlite',
            filename='testdb.sql',
            create_db=True
        )

        self.initial_date = datetime.datetime(year=2020,
                                              month=1,
                                              day=1,
                                              hour=10,
                                              minute=00,
                                              second=00,
                                              microsecond=00)
        self.time_to_add = datetime.timedelta(minutes=15)
        self.record_size_mb = 25.19535

    def tearDown(self):
        self.db_test.drop_all_tables(with_all_data=True)

    @db_session
    def __populate_test_db(self):

        # Archive 01 - Already Uploaded and Removed
        self.archive_01 = self.db_test.Archive(
            creation=self.initial_date + (60 * self.time_to_add),
            local_path='/data/archive_01.zip',
            size=self.record_size_mb * 3,
            remote_path='https://amazon.s3/archive_01',
            uploaded=True,
            removed=True
        )

        # Archive 02 - Not Uploaded and Not Removed
        self.archive_02 = self.db_test.Archive(
            creation=self.initial_date + (120 * self.time_to_add),
            local_path='/data/archive_02.zip',
            size=self.record_size_mb * 3,
            remote_path='https://amazon.s3/archive_01',
            uploaded=False,
            removed=False
        )

        # Records related to Archive 01 - Not Removed
        self.record_01 = self.db_test.Record(
            start=self.initial_date,
            end=self.initial_date + self.time_to_add,
            size=self.record_size_mb,
            path='/data/record_01.wav',
            status=RecordStatus(2).name,
            removed=False,
            archive=self.archive_01
        )

        self.record_02 = self.db_test.Record(
            start=self.initial_date + self.time_to_add,
            end=self.initial_date + (2 * self.time_to_add),
            size=self.record_size_mb,
            path='/data/record_02.wav',
            status=RecordStatus(2).name,
            removed=False,
            archive=self.archive_01
        )

        self.record_03 = self.db_test.Record(
            start=self.initial_date + (2 * self.time_to_add),
            end=self.initial_date + (3 * self.time_to_add),
            size=self.record_size_mb,
            path='/data/record_03.wav',
            status=RecordStatus(2).name,
            removed=False,
            archive=self.archive_01
        )

        # Records related to Archive 02 - Removed
        self.record_04 = self.db_test.Record(
            start=self.initial_date + (3 * self.time_to_add),
            end=self.initial_date + (4 * self.time_to_add),
            size=self.record_size_mb,
            path='/data/record_04.wav',
            status=RecordStatus(2).name,
            removed=True,
            archive=self.archive_02
        )

        self.record_05 = self.db_test.Record(
            start=self.initial_date + (4 * self.time_to_add),
            end=self.initial_date + (5 * self.time_to_add),
            size=self.record_size_mb,
            path='/data/record_05.wav',
            status=RecordStatus(2).name,
            removed=True,
            archive=self.archive_02
        )

        self.record_06 = self.db_test.Record(
            start=self.initial_date + (5 * self.time_to_add),
            end=self.initial_date + (6 * self.time_to_add),
            size=self.record_size_mb,
            path='/data/record_06.wav',
            status=RecordStatus(2).name,
            removed=True,
            archive=self.archive_02
        )

        # Records without any Archive
        self.record_07 = self.db_test.Record(
            start=self.initial_date + (6 * self.time_to_add),
            end=self.initial_date + (7 * self.time_to_add),
            size=self.record_size_mb,
            path='/data/record_07.wav',
            status=RecordStatus(1).name,
            removed=False
        )

        self.record_08 = self.db_test.Record(
            start=self.initial_date + (7 * self.time_to_add),
            end=self.initial_date + (8 * self.time_to_add),
            size=self.record_size_mb,
            path='/data/record_08.wav',
            status=RecordStatus(1).name,
            removed=False
        )

        self.record_09 = self.db_test.Record(
            start=self.initial_date + (8 * self.time_to_add),
            end=self.initial_date + (9 * self.time_to_add),
            size=self.record_size_mb,
            path='/data/record_09.wav',
            status=RecordStatus(1).name,
            removed=False
        )

    @db_session
    def test_get_recorded_entries(self):
        self.__populate_test_db()
        q = get_recorded_entries(self.db_test)

        self.assertEqual(
            len(q),
            3
        )

    @db_session
    def test_get_records_from_archive(self):
        self.__populate_test_db()
        q = get_records_from_archive(self.archive_01, self.db_test)

        self.assertEqual(
            len(q),
            3
        )

    @db_session
    def test_get_records_uploaded(self):
        self.__populate_test_db()
        q = get_records_uploaded(self.db_test)

        self.assertEqual(
            len(q),
            3
        )

    @db_session
    def test_get_archives_uploaded(self):
        self.__populate_test_db()
        q = get_archives_uploaded(self.db_test)

        self.assertEqual(
            len(q),
            1
        )

    @db_session
    def test_get_archives_not_uploaded(self):
        self.__populate_test_db()
        q = get_archives_not_uploaded(self.db_test)

        self.assertEqual(
            len(q),
            1
        )

    @db_session
    def test_get_local_archive_files(self):
        self.__populate_test_db()
        q = get_local_archive_files(self.db_test)

        self.assertEqual(
            len(q),
            1
        )

    @db_session
    def test_get_local_record_files(self):
        self.__populate_test_db()
        q = get_local_record_files(self.db_test)

        self.assertEqual(
            len(q),
            6
        )

    @db_session
    def test_get_record_by_date(self):
        self.__populate_test_db()

        start_date_01 = '2020-01-01 10:00'
        end_date_01 = '2020-01-01 10:30'

        start_date_02 = '2020-01-01 10:07'
        end_date_02 = '2020-01-01 10:53'

        start_date_03 = '2020-01-01 11:30:01'
        end_date_03 = '2020-01-01 13:00'

        start_date_04 = '2020-01-01'
        end_date_04 = '2025-01-02'

        # Should return Record 01 and Record 02
        q_01 = get_record_by_date(self.db_test, start_date_01, end_date_01,
                                  timez='America/Santiago')
        self.assertTrue(q_01.get(str(self.record_01.id)))
        self.assertTrue(q_01.get(str(self.record_02.id)))

        # Should return Record 01 to Record 04
        q_02 = get_record_by_date(self.db_test, start_date_02, end_date_02,
                                  timez='America/Santiago')
        self.assertTrue(q_02.get(str(self.record_01.id)))
        self.assertTrue(q_02.get(str(self.record_02.id)))
        self.assertTrue(q_02.get(str(self.record_03.id)))
        self.assertTrue(q_02.get(str(self.record_04.id)))

        # Should return Record 07 to Record 09
        q_03 = get_record_by_date(self.db_test, start_date_03, end_date_03,
                                  timez='America/Santiago')
        self.assertTrue(q_03.get(str(self.record_07.id)))
        self.assertTrue(q_03.get(str(self.record_08.id)))
        self.assertTrue(q_03.get(str(self.record_09.id)))

        # Should Return ALL Records
        q_04 = get_record_by_date(self.db_test, start_date_04, end_date_04,
                                  timez='America/Santiago')
        self.assertTrue(q_04.get(str(self.record_01.id)))
        self.assertTrue(q_04.get(str(self.record_02.id)))
        self.assertTrue(q_04.get(str(self.record_03.id)))
        self.assertTrue(q_04.get(str(self.record_04.id)))
        self.assertTrue(q_04.get(str(self.record_05.id)))
        self.assertTrue(q_04.get(str(self.record_06.id)))
        self.assertTrue(q_04.get(str(self.record_07.id)))
        self.assertTrue(q_04.get(str(self.record_08.id)))
        self.assertTrue(q_04.get(str(self.record_09.id)))
