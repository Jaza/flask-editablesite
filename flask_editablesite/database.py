# -*- coding: utf-8 -*-
"""Database module, including the SQLAlchemy database object and DB-related
utilities.
"""

from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship, validates

from slugify import slugify

from .extensions import db
from .compat import basestring

# Alias common SQLAlchemy names
Column = db.Column
relationship = relationship


class CRUDMixin(object):
    """Mixin that adds convenience methods for CRUD (create, read, update, delete)
    operations.
    """

    @classmethod
    def create(cls, **kwargs):
        """Create a new record and save it the database."""
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        """Update specific fields of a record."""
        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        """Save the record."""
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        """Remove the record from the database."""
        db.session.delete(self)
        return commit and db.session.commit()


class Model(CRUDMixin, db.Model):
    """Base model class that includes CRUD convenience methods."""
    __abstract__ = True


# From Mike Bayer's "Building the app" talk
# https://speakerdeck.com/zzzeek/building-the-app
class SurrogatePK(object):
    """A mixin that adds a surrogate integer 'primary key' column named
    ``id`` to any declarative-mapped class.
    """
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    @classmethod
    def get_by_id(cls, id):
        if any(
            (isinstance(id, basestring) and id.isdigit(),
             isinstance(id, (int, float))),
        ):
            return cls.query.get(int(id))
        return None


def ReferenceCol(tablename, nullable=False, pk_name='id', **kwargs):
    """Column that adds primary key foreign key reference.

    Usage: ::

        category_id = ReferenceCol('category')
        category = relationship('Category', backref='categories')
    """
    return db.Column(
        db.ForeignKey("{0}.{1}".format(tablename, pk_name)),
        nullable=nullable, **kwargs)


class Slugged(object):
    title = db.Column(db.String(255))
    slug = db.Column(db.String(255))

    @validates('slug')
    def validate_slug(self, key, value):
        if value == 'admin':
            raise IntegrityError('', '', "Slug 'admin' is not allowed.")
        return value


def update_slug_before_save(mapper, connection, target):
    if target.slug:
        target.slug = slugify(target.slug, to_lower=True)
    else:
        target.slug = slugify(target.title, to_lower=True)


class TimeStamped(object):
    created_at = db.Column(db.DateTime())
    updated_at = db.Column(db.DateTime())

    @property
    def created_at_formatted(self):
        from flask_babel import format_datetime

        return (self.created_at
                and format_datetime(self.created_at, 'long')
                or None)

    @property
    def updated_at_formatted(self):
        from flask_babel import format_datetime

        return (self.updated_at
                and format_datetime(self.updated_at, 'long')
                or None)


def update_timestamps_before_insert(mapper, connection, target):
    ts = datetime.utcnow()
    target.created_at = ts
    target.updated_at = ts


def update_timestamps_before_update(mapper, connection, target):
    target.updated_at = datetime.utcnow()


class Confirmable(object):
    active = db.Column(db.Boolean(), default=False)
    confirmed_at = db.Column(db.DateTime())

    @property
    def confirmed_at_formatted(self):
        from flask_babel import format_datetime

        return (self.confirmed_at
                and format_datetime(self.confirmed_at, 'long')
                or None)


def update_confirmedat_before_save(mapper, connection, target):
    if target.active and not target.confirmed_at:
        target.confirmed_at = datetime.utcnow()
    elif target.confirmed_at and not target.active:
        target.active = True
