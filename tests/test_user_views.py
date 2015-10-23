# -*- coding: utf-8 -*-
"""Testing of user views."""

from flask_webtest import TestApp

from flask import url_for

from flask_editablesite.user.models import User


def test_login_returns_200(user, testapp):
    # Goes to homepage
    res = testapp.get("/")
    # Fills out login form
    form = res.forms['loginForm']
    form['email'] = user.email
    form['password'] = 'myprecious'
    # Submits
    res = form.submit().follow()
    assert res.status_code == 200


def test_login_returns_200_sessionstore(app_sessionstore):
    app = app_sessionstore
    with app.test_request_context():
        testapp = TestApp(app_sessionstore)

        # Goes to homepage
        res = testapp.get("/")
        # Fills out login form
        form = res.forms['loginForm']

        user = User.sessionstore_user()

        form['email'] = user.email
        form['password'] = app.config['SESSIONSTORE_USER_PASSWORD']
        # Submits
        res = form.submit().follow()
        assert res.status_code == 200


def test_logout_alert_visible(user, testapp):
    res = testapp.get("/")
    # Fills out login form
    form = res.forms['loginForm']
    form['email'] = user.email
    form['password'] = 'myprecious'
    # Submits
    res = form.submit().follow()
    res = testapp.get(url_for('public.logout')).follow()
    # sees alert
    assert 'You are logged out.' in res


def test_login_errormsg_if_pw_wrong(user, testapp):
    # Goes to homepage
    res = testapp.get("/")
    # Fills out login form, password incorrect
    form = res.forms['loginForm']
    form['email'] = user.email
    form['password'] = 'wrong'
    # Submits
    res = form.submit()
    # Redirects home
    res = res.follow()
    # sees error
    assert "Invalid password" in res


def test_login_errormsg_if_email_unknown(user, testapp):
    # Goes to homepage
    res = testapp.get("/")
    # Fills out login form, password incorrect
    form = res.forms['loginForm']
    form['email'] = 'email'
    form['password'] = 'myprecious'
    # Submits
    res = form.submit()
    # Redirects home
    res = res.follow()
    # sees error
    assert "Unknown email" in res
