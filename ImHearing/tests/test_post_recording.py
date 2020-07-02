""" Test post-recording routines in ImHearing/pre_recording.py
"""

import datetime
import unittest
from enum import Enum
from os import path, remove

from moto import mock_s3
import boto3
from pony.orm import db_session

from ImHearing import post_recording
from ImHearing.database.models import define_db
from ImHearing.database.query import (get_recorded_entries,
                                      get_archives_uploaded)


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
    def __creates_records_without_archives(self, create_files=True):
        self.record_without_arch_01 = self.db_test.Record(
            start=self.initial_date + (6 * self.time_to_add),
            end=self.initial_date + (7 * self.time_to_add),
            size=self.record_size_mb,
            path='./record_without_arch_01.wav',
            status=RecordStatus(1).name,
            removed=False
        )

        self.record_without_arch_02 = self.db_test.Record(
            start=self.initial_date + (7 * self.time_to_add),
            end=self.initial_date + (8 * self.time_to_add),
            size=self.record_size_mb,
            path='./record_without_arch_02.wav',
            status=RecordStatus(1).name,
            removed=False
        )

        self.record_without_arch_03 = self.db_test.Record(
            start=self.initial_date + (8 * self.time_to_add),
            end=self.initial_date + (9 * self.time_to_add),
            size=self.record_size_mb,
            path='./record_without_arch_03.wav',
            status=RecordStatus(1).name,
            removed=False
        )

        if create_files:
            for file in ['./record_without_arch_01.wav',
                         './record_without_arch_02.wav',
                         './record_without_arch_03.wav']:
                f = open(file, "w+")
                f.close()

    @db_session
    def __creates_records_to_remove(self, create_files=True):
        self.archive_local_fs = self.db_test.Archive(
            creation=self.initial_date + (60 * self.time_to_add),
            local_path='./archive_01.zip',
            size=self.record_size_mb * 3,
            remote_path='',
            uploaded=True,
            removed=False
        )

        self.record_in_fs_01 = self.db_test.Record(
            start=self.initial_date + (6 * self.time_to_add),
            end=self.initial_date + (7 * self.time_to_add),
            size=self.record_size_mb,
            path='./record_in_fs_01.wav',
            status=RecordStatus(2).name,
            removed=False,
            archive=self.archive_local_fs
        )

        self.record_in_fs_02 = self.db_test.Record(
            start=self.initial_date + (7 * self.time_to_add),
            end=self.initial_date + (8 * self.time_to_add),
            size=self.record_size_mb,
            path='./record_in_fs_02.wav',
            status=RecordStatus(2).name,
            removed=False,
            archive=self.archive_local_fs
        )

        self.record_in_fs_03 = self.db_test.Record(
            start=self.initial_date + (8 * self.time_to_add),
            end=self.initial_date + (9 * self.time_to_add),
            size=self.record_size_mb,
            path='./record_in_fs_03.wav',
            status=RecordStatus(2).name,
            removed=False,
            archive=self.archive_local_fs
        )

        if create_files:
            for file in ['./record_in_fs_01.wav',
                         './record_in_fs_02.wav',
                         './record_in_fs_03.wav']:
                f = open(file, "w+")
                f.close()

    @db_session
    def __creates_archives(self, create_files=True):
        # Archive 01 - Already Uploaded and Removed
        self.archive_01 = self.db_test.Archive(
            creation=self.initial_date + (60 * self.time_to_add),
            local_path='./archive_01.zip',
            size=self.record_size_mb * 3,
            remote_path='https://amazon.s3/archive_01',
            uploaded=True,
            removed=True
        )

        # Archive 02 - Not Uploaded and Not Removed
        self.archive_02 = self.db_test.Archive(
            creation=self.initial_date + (120 * self.time_to_add),
            local_path='./archive_02.zip',
            size=self.record_size_mb * 3,
            remote_path='',
            uploaded=False,
            removed=False
        )

        if create_files:
            f = open('./archive_02.zip', 'w+')
            f.close()

    @db_session
    def test_archive_records(self):
        config_01 = {
            'GLOBAL': {
                'record_path': '.',
                'archive_path': '.',
                'storage_usage': '0',
                'records_count': '5',
                'log_file': '/var/log/ImHearing.log',
                'record_period': '30'
            }
        }
        self.assertFalse(
            post_recording.archive_records(self.db_test, config_01['GLOBAL'])
        )

        self.__creates_records_without_archives()

        # Must appear 3 records
        local_records = get_recorded_entries(self.db_test)
        self.assertEqual(
            len(local_records),
            3
        )

        # Now we add the records to an Archive - No records can be shown
        archive = post_recording.archive_records(self.db_test,
                                                 config_01['GLOBAL'])
        local_records = get_recorded_entries(self.db_test)
        self.assertEqual(
            len(local_records),
            0
        )
        remove(archive.local_path)

        # Removes all .wav
        for file in ['./record_without_arch_01.wav',
                     './record_without_arch_02.wav',
                     './record_without_arch_03.wav']:
            remove(file)

    @db_session
    def test_remove_uploaded_archives(self):

        # Must return Zero when there is no Archive to Upload
        self.assertEqual(
            post_recording.remove_uploaded_archives(self.db_test),
            0
        )

        self.__creates_archives()

        self.assertTrue(
            path.isfile(self.archive_02.local_path)
        )

        archive_list = post_recording.remove_uploaded_archives(self.db_test)
        self.assertEqual(
            len(archive_list),
            1
        )
        self.assertFalse(
            path.isfile(self.archive_02.local_path)
        )

    @db_session
    def test_remove_uploaded_records(self):

        # Must return Zero when there is no Archive to Upload
        self.assertEqual(
            post_recording.remove_uploaded_records(self.db_test),
            0
        )

        self.__creates_records_to_remove()
        removed_records = post_recording.remove_uploaded_records(self.db_test)

        self.assertIn(
            self.record_in_fs_01,
            removed_records
        )
        self.assertIn(
            self.record_in_fs_02,
            removed_records
        )
        self.assertIn(
            self.record_in_fs_03,
            removed_records
        )

    @db_session
    def test_upload_archive(self):
        mock = mock_s3()
        mock.start()

        config_01 = {
            'AWS': {
                's3_bucket_name': 'my_bucket',
                's3_region': 'eu-west-1',
                'price_per_gb': '0.0023',
                'budget_cost': '30',
            }
        }

        self.assertTrue(
            post_recording.upload_archive(self.db_test, config_01['AWS'])
        )

        self.__creates_archives()
        s3 = boto3.resource('s3')
        s3.create_bucket(Bucket=config_01['AWS']['s3_bucket_name'])
        self.assertTrue(
            post_recording.upload_archive(self.db_test, config_01['AWS']))
        mock.stop()
        remove('./archive_02.zip')

        # Check if the Archive entry changed correctly
        self.assertEqual(
            2,
            len(get_archives_uploaded(self.db_test))
        )
