""" This file contains routines to display and get data from DB
"""

from flask import Flask, render_template
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


@app.route('/')
def index():
    return render_template('index.html')


@db_session
@app.route('/record/<record_id>')
def get_record_id(record_id):
    return "Some record UUID"


@db_session
@app.route('/record/')
def get_all_records():
    return query.get_all_records(db)


@db_session
@app.route('/archive/<archive_id>')
def get_archive_id(archive_id):
    return "archives"


@db_session
@app.route('/archive/')
def get_all_archives():
    return query.get_all_archives(db)


@app.route('/query/<date>')
def get_query_by_date(date):
    return "dates"


# Todo: Remove debug after implementation
app.run(debug=True)
