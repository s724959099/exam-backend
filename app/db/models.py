"""
db with postgres
"""

import datetime

from config import config
from pony.orm import Database, Optional, Required

db = Database()


class User(db.Entity):
    """User table"""
    _table_ = 'User'
    email = Required(str, unique=True, index=True)
    name = Required(str)
    created_at = Required(datetime.datetime, default=datetime.datetime.now)
    updated_at = Optional(datetime.datetime, nullable=True)
    deleted = Optional(bool, default=False)
    deleted_at = Optional(datetime.datetime, nullable=True)


db.bind(
    provider='postgres',
    user=config.get('DB_USER'),
    password=config.get('DB_PASSWORD'),
    host=config.get('DB_HOST'),
    port=config.get('DB_PORT'),
    database=config.get('DB_DATABASE_NAME'))
db.generate_mapping(create_tables=True)
