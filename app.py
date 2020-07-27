""" This file contains routines to display and get data from DB
"""

from flask import Flask, render_template, Blueprint
from pony.orm import db_session

from ImHearing.database import models, query
from ImHearing import reader

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


@db_session
@v1.route('/records/<record_id>')
def get_record_id(record_id):
    return "Some record UUID {}".format(record_id)


@db_session
@v1.route('/records/')
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


@db_session
@v1.route('/archives/<archive_id>')
def get_archive_id(archive_id):
    return "Some archive UUID {}".format(archive_id)


@db_session
@v1.route('/archives/')
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


@v1.route('/query/<date>')
def get_query_by_date(date):
    return "dates"


app.register_blueprint(v1, url_prefix="/v1")


# Todo: Remove debug after implementation
app.run(debug=True)
