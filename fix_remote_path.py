""" Fixes the Remote Path in archives
"""

from pony.orm import db_session
from pony.orm.dbapiprovider import DatabaseError

from ImHearing import reader
from ImHearing.database import models, query

# Get DB Configuration
DB_CONFIG, db_ret = reader.db_config()
AWS_CONFIG, aws_ret = reader.aws_config()


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


def generate_remote_path(cur_uuid):
    """

    :param cur_uuid:
    :return:
    """

    remote_path = "https://%s.%s.amazonaws.com/%s" % (
        aws_ret['s3_bucket_name'],
        aws_ret['s3_region'],
        cur_uuid)
    return remote_path


def main():

    list_of_archives = query.get_archives_uploaded(db)
    for archive in list_of_archives:
        p = generate_remote_path(str(archive.id))
        print(p)


if __name__ == '__main__':
    main()
