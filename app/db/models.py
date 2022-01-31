"""
db with postgres
"""

import datetime

from config import config
from pony.orm import Database, Optional, Required, Set
from utils import encrypt

db = Database()


class User(db.Entity):
    """User table"""
    _table_ = 'User'
    email = Required(str, unique=True, index=True)
    name = Required(str)
    register_from = Required(int)  # 1: web|2: facebook|3: google
    password = Optional(str, nullable=True)  # only web
    salt = Optional(str, nullable=True)  # only web
    verify = Required(bool, default=False)  # verification from email
    verify_id = Optional(str, nullable=True)  # for web url
    login_count = Required(int, default=0)
    last_login_time = Required(datetime.datetime, default=datetime.datetime.now)
    created_at = Required(datetime.datetime, default=datetime.datetime.now)
    updated_at = Optional(datetime.datetime, nullable=True)
    deleted = Optional(bool, default=False)
    deleted_at = Optional(datetime.datetime, nullable=True)
    records = Set('UserActivieRecord')

    def check_password(self, raw_password: str) -> bool:
        """
        Compare with encrypted password
        Args:
            raw_password: raw passowrd
        Returns:
             bool
        """
        if self.password is None:
            return False
        salt_ = encrypt.transfer_salt_str_to_bytes(self.salt)
        hashed_password = encrypt.get_hash(raw_password, salt_)
        return hashed_password == self.password


class UserActivieRecord(db.Entity):
    """UserActivieRecord table"""
    _table_ = 'UserActivieRecord'
    user = Required(User)
    created_at = Required(datetime.datetime, default=datetime.datetime.now)


db.bind(
    provider='postgres',
    user=config.get('DB_USER'),
    password=config.get('DB_PASSWORD'),
    host=config.get('DB_HOST'),
    port=config.get('DB_PORT'),
    database=config.get('DB_DATABASE_NAME'))
db.generate_mapping(create_tables=True)
