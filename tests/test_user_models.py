# -*- coding: utf-8 -*-
"""Model unit tests."""

import datetime as dt

from flask_editablesite.user.models import User
from .factories import UserFactory


def test_user_get_by_id():
    user = User('foo', 'foo@bar.com')
    user.save()

    retrieved = User.get_by_id(user.id)
    assert retrieved == user

    user.delete()


def test_user_created_at_defaults_to_datetime():
    user = User(email='foo@bar.com')
    user.save()
    assert bool(user.created_at)
    assert isinstance(user.created_at, dt.datetime)

    user.delete()


def test_user_password_is_nullable():
    user = User(email='foo@bar.com')
    user.save()
    assert user.password is None

    user.delete()


def test_user_factory(db):
    user = UserFactory(password="myprecious")
    db.session.commit()
    assert bool(user.email)
    assert bool(user.created_at)
    assert user.active is True
    assert user.check_password('myprecious')


def test_user_check_password():
    user = User.create(email="foo@bar.com",
                       password="foobarbaz123")
    assert user.check_password('foobarbaz123') is True
    assert user.check_password("barfoobaz") is False

    user.delete()


def test_user_full_name():
    user = UserFactory(first_name="Foo", last_name="Bar")
    assert user.full_name == "Foo Bar"
