# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""

import pytest
from flask_webtest import TestApp

from flask_editablesite.settings import TestConfig
from flask_editablesite.app import create_app
from flask_editablesite.database import db as _db

from .factories import UserFactory


@pytest.yield_fixture(scope='session')
def app():
    _app = create_app(TestConfig)
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


class SessionStoreTestConfig(TestConfig):
    USE_SESSIONSTORE_NOT_DB = True


@pytest.fixture(scope='session')
def app_sessionstore():
    return create_app(SessionStoreTestConfig)


@pytest.fixture(scope='session')
def testapp(app):
    """A Webtest app."""
    return TestApp(app)


@pytest.yield_fixture(scope='session')
def db(app):
    _db.app = app
    with app.app_context():
        _db.session.remove()
        _db.drop_all()
        _db.create_all()

    yield _db

    _db.session.remove()
    _db.drop_all()

    # This dispose() call is needed to avoid the DB locking
    # between tests.
    # Thanks to:
    # http://stackoverflow.com/a/18293157/2066849
    _db.get_engine(_db.app).dispose()


@pytest.fixture(scope='session')
def user(db):
    user = UserFactory(password='myprecious')
    db.session.commit()
    return user
