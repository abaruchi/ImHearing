""" This file contains routines to display and get data from DB
"""

from uuid import UUID

import validators
from flask import Blueprint, Flask, render_template
from pony.orm import db_session

from ImHearing import reader
from ImHearing.database import models, query

DB_CONFIG, db_ret = reader.db_config()

db = models.define_db(
    provider='sqlite',
    filename=DB_CONFIG['db_path'],
    create_db=True
)

app = Flask(__name__)
v1 = Blueprint("version1", "version1")


@app.route('/')
def index():
    return render_template('index.html')


@v1.route('/records/<record_id>')
@db_session
def get_record_id(record_id):

    out = {}
    if validators.uuid(record_id):
        record_uuid = UUID(record_id)
        rec = query.get_single_record(db, record_uuid.bytes)
        if rec:
            out = {
                'Record_ID': str(rec.id),
                'Start': rec.start,
                'End': rec.end,
                'Size': rec.size,
                'Path': rec.size,
                'Status': rec.status,
                'Removed': rec.removed
            }
    return out


@v1.route('/records/')
@db_session
def get_all_records():
    list_of_records = query.get_all_records(db)
    records_dict = dict()

    for record in list_of_records:
        records_dict[str(record.id)] = {
            'ID': str(record.id),
            'Status': record.status,
            'Start': record.start,
            'End': record.end,
            'Size': record.size
        }
        if record.archive is not None:
            records_dict[str(record.id)]['Archive'] = str(record.archive.id)

        else:
            records_dict[str(record.id)]['Archive'] = None

    return render_template('recordslist.html', records=records_dict)


@v1.route('/archives/<archive_id>')
@db_session
def get_archive_id(archive_id):

    out = {}
    if validators.uuid(archive_id):
        archive_uuid = UUID(archive_id)
        arc = query.get_single_archive(db, archive_uuid.bytes)
        if arc:
            records_out = dict()
            for rec in arc.records:
                records_out[str(rec.id)] = {
                    'Start': rec.start,
                    'End': rec.end
                }
            out = {
                'Archive_ID': arc.id,
                'Creation': arc.creation,
                'Size': arc.size,
                'RemotePath': arc.remote_path,
                'Removed': arc.removed,
                'RecordsArchived': records_out
            }
    return out


@v1.route('/archives/')
@db_session
def get_all_archives():
    list_of_archives = query.get_all_archives(db)
    archives_dict = dict()

    for archive in list_of_archives:
        archives_dict[str(archive.id)] = {
            'ID': str(archive.id),
            'Created': archive.creation,
            'LocalPath': archive.local_path,
            'RemotePath': archive.remote_path
        }

    return render_template('archiveslist.html', archives=archives_dict)


@v1.route('/query/<datetime>')
@db_session
def get_query_by_date(datetime):

    parameter = datetime.split('_')
    start_date = parameter[0]
    end_date = parameter[1]

    records = query.get_record_by_date(
        db,
        start_date,
        end_date
    )

    return render_template('querylist.html', records=records)


app.register_blueprint(v1, url_prefix="/v1")


# Todo: Remove debug after implementation
app.run(debug=True)
