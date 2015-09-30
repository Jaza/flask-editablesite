# -*- coding: utf-8 -*-
import datetime as dt

from flask import current_app as app
from flask_login import UserMixin
from sqlalchemy import event

from flask_editablesite.extensions import bcrypt
from flask_editablesite.database import (
    Column,
    db,
    Model,
    SurrogatePK,
    TimeStamped,
    Confirmable,
    update_timestamps_before_insert,
    update_timestamps_before_update,
    update_confirmedat_before_save,
)


class User(UserMixin, SurrogatePK, TimeStamped, Confirmable, Model):
    __tablename__ = 'users'

    email = Column(db.String(255), unique=True, nullable=False)
    password = Column(db.String(255), nullable=True)
    first_name = Column(db.String(255), nullable=True)
    last_name = Column(db.String(255), nullable=True)

    def __init__(self, email, password=None, **kwargs):
        db.Model.__init__(self, email=email, **kwargs)
        if password:
            self.set_password(password)
        else:
            self.password = None

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, value):
        return bcrypt.check_password_hash(self.password, value)

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return "{0} {1}".format(self.first_name, self.last_name)

        return ""

    @property
    def full_name_or_email(self):
        return self.full_name or self.email

    def __repr__(self):
        return '{0} <{1}>'.format(self.full_name, self.email)

    @classmethod
    def sessionstore_user(cls):
        """A dummy user object to represent the logged-in user when we're set to 'sessionstore' instead of 'db'."""

        return cls(email=app.config['SESSIONSTORE_USER_EMAIL'],
            first_name=app.config['SESSIONSTORE_USER_FIRST_NAME'],
            last_name=app.config['SESSIONSTORE_USER_LAST_NAME'],
            active=True)


event.listen(User, 'before_insert', update_timestamps_before_insert)
event.listen(User, 'before_update', update_timestamps_before_update)

event.listen(User, 'before_insert', update_confirmedat_before_save)
event.listen(User, 'before_update', update_confirmedat_before_save)
