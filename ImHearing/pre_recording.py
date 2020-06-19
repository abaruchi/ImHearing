""" Routines check if conditions are satisfied before start recording
"""

from shutil import disk_usage

from pony.orm import db_session, sum

from ImHearing.database import query


@db_session
def check_aws_budget(db, aws_config):
    """
    This routine checks if the budget used in AWS was exceeded or not
    :param db: Pony DB Connection
    :param aws_config: AWS Config Dict
    :return: Amount to reach budget (positive) or amount already over
            (negative)
    """

    budget_max = int(aws_config['budget_cost'])
    if budget_max == 0:
        return float('Inf')

    # Get all Archives already uploaded to AWS
    archives_uploaded = query.get_archives_uploaded(db)
    uploaded_gb = (sum(o.size for o in archives_uploaded) // 1024)

    current_amount = float(aws_config['price_per_gb']) * uploaded_gb
    return budget_max - current_amount


@db_session
def check_fs_usage(db, global_config):
    """
    This routine verifies if the fs usage is under or above the configured in
    config file.
    :param db: Pony DB Connection
    :param global_config: Global Config Dict
    :return: Amount to reach the FS usage (positive) or amount already over
            the fs usage (negative)
    """

    max_fs_usage = int(global_config['storage_usage'])
    if max_fs_usage == 0:
        return float('Inf')

    # List of records in local disk
    local_records_list = query.get_local_record_files(db)
    local_records_mb = sum(o.size for o in local_records_list)

    return max_fs_usage - local_records_mb


@db_session
def check_record_count(db, global_config):
    """
    This routine verifies if the number of records is under or above the
    configured in config file
    :param db: Pony DB Connection
    :param global_config: Global Config Dict
    :return: Number of records to reach the total or number of records over
            the total number of records
    """

    max_count = int(global_config['records_count'])
    if max_count == 0:
        return float('Inf')

    records_count = len(query.get_local_record_files(db))

    return max_count - records_count
