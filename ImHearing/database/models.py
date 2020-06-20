from datetime import datetime
from uuid import UUID

from pony.orm import Database, Optional, PrimaryKey, Required, Set


def define_entities(db):

    class User(db.Entity):
        id = PrimaryKey(UUID, auto=True)
        name = Required(str, 255)
        email = Optional(str)
        passord = Optional(str, 255)
        last_login = Optional(datetime)
        tokens = Set('Token')

    class Record(db.Entity):
        id = PrimaryKey(UUID, auto=True)
        start = Required(datetime)
        end = Optional(datetime)
        size = Optional(float)
        path = Optional(str)
        status = Optional(str)
        removed = Required(bool, default=False)
        archive = Optional('Archive')

    class Archive(db.Entity):
        id = PrimaryKey(UUID, auto=True)
        creation = Optional(datetime)
        local_path = Required(str)
        size = Optional(float)
        remote_path = Optional(str, default='')
        uploaded = Optional(bool, default=False)
        removed = Required(bool, default=False)
        records = Set(Record)

    class Token(db.Entity):
        id = PrimaryKey(UUID, auto=True)
        expiration = Required(datetime)
        user = Required(User)


def define_db(**db_params):
    db = Database(**db_params)
    define_entities(db)
    db.generate_mapping(create_tables=True)

    return db