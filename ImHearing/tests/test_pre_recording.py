""" Test pre-recording routines in ImHearing/pre_recording.py
"""

import datetime
import unittest
from enum import Enum

from pony.orm import db_session

from ImHearing.database.models import define_db
from ImHearing import pre_recording


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

        self.config_dict = {
            'AWS': {
                's3_bucket_name': 'test_bucket',
                's3_region': 'test_region',
                'price_per_gb': '0.50',
                'budget_cost': '15.50'
            },
            'GLOBAL': {
                'record_path': '/tmp/',
                'archive_path': '/tmp/',
                'storage_usage': '100',
                'records_count': '5',
                'log_file': '/var/log/ImHearing.log',
                'record_period': '30'
            }
        }

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

    def test_check_fs_usage(self):
        self.__populate_test_db()
        config_01 = {
            'GLOBAL': {
                'record_path': '/tmp/',
                'archive_path': '/tmp/',
                'storage_usage': '0',
                'records_count': '5',
                'log_file': '/var/log/ImHearing.log',
                'record_period': '30'
            }
        }
        usage_01 = pre_recording.check_fs_usage(self.db_test,
                                                config_01['GLOBAL'])
        self.assertEqual(
            usage_01,
            float('Inf')
        )

        config_02 = {
            'GLOBAL': {
                'record_path': '/tmp/',
                'archive_path': '/tmp/',
                'storage_usage': '300',
                'records_count': '5',
                'log_file': '/var/log/ImHearing.log',
                'record_period': '30'
            }
        }
        usage_02 = pre_recording.check_fs_usage(self.db_test,
                                                config_02['GLOBAL'])
        # Should return (300 - (6 * size_of_record))
        self.assertEqual(
            usage_02,
            148.8279
        )

    def test_check_record_count(self):
        self.__populate_test_db()

        config_01 = {
            'GLOBAL': {
                'record_path': '/tmp/',
                'archive_path': '/tmp/',
                'storage_usage': '0',
                'records_count': '0',
                'log_file': '/var/log/ImHearing.log',
                'record_period': '30'
            }
        }
        usage_01 = pre_recording.check_record_count(self.db_test,
                                                    config_01['GLOBAL'])
        self.assertEqual(
            usage_01,
            float('Inf')
        )

        config_02 = {
            'GLOBAL': {
                'record_path': '/tmp/',
                'archive_path': '/tmp/',
                'storage_usage': '300',
                'records_count': '10',
                'log_file': '/var/log/ImHearing.log',
                'record_period': '30'
            }
        }
        usage_02 = pre_recording.check_record_count(self.db_test,
                                                    config_02['GLOBAL'])

        # # Should return (10 - 6)
        self.assertEqual(
            usage_02,
            4
        )

    def test_check_aws_budget(self):

        self.__populate_test_db()

        config_01 = {
            'AWS': {
                's3_bucket_name': 'test_bucket',
                's3_region': 'test_region',
                'price_per_gb': '0.50',
                'budget_cost': '15.50'
            }
        }
        usage_01 = pre_recording.check_aws_budget(self.db_test,
                                                  config_01['AWS'])
        self.assertEqual(
            usage_01,
            15.463092749023437
        )

        config_02 = {
            'AWS': {
                's3_bucket_name': 'test_bucket',
                's3_region': 'test_region',
                'price_per_gb': '0.50',
                'budget_cost': '0'
            }
        }
        usage_02 = pre_recording.check_aws_budget(self.db_test,
                                                  config_02['AWS'])
        self.assertEqual(
            usage_02,
            float('Inf')
        )

