# -*- coding: utf-8 -*-
import pytest

from flask_editablesite.public.forms import LoginForm
from .factories import UserFactory


def test_login_success(user):
    user.set_password('example')
    user.save()
    form = LoginForm(email=user.email, password='example')
    assert form.validate() is True
    assert form.user == user


def test_login_unknown_email(db):
    form = LoginForm(email='unknown', password='example')
    assert form.validate() is False
    assert 'Unknown email' in form.email.errors
    assert form.user is None


def test_login_invalid_password(user):
    user.set_password('example')
    user.save()
    form = LoginForm(email=user.email, password='wrongpassword')
    assert form.validate() is False
    assert 'Invalid password' in form.password.errors


def test_login_inactive_user(user):
    user.active = False
    user.confirmed_at = None
    user.set_password('example')
    user.save()
    # Correct email and password, but user is not activated
    form = LoginForm(email=user.email, password='example')
    assert form.validate() is False
    assert (
        'User {0} not activated'.format(user.full_name_or_email)
        in form.email.errors)
