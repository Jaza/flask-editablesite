# -*- coding: utf-8 -*-
"""Test editable view routes."""

from datetime import datetime, timedelta
import pytest
import random
from flask_webtest import TestApp

from flask import (session, url_for)

from flask_editablesite.contentblock.models import (
    ShortTextContentBlock,)
from flask_editablesite.event.models import Event
from flask_editablesite.user.models import User


def test_home_textcontentblock_update_visible(app, user, testapp):
    # Goes to homepage
    res = testapp.get("/")
    # Fills out login form
    form = res.forms['loginForm']
    form['email'] = user.email
    form['password'] = 'myprecious'
    # Submits
    res = form.submit().follow()

    default_content = ShortTextContentBlock.default_content()
    assert default_content['site-byline'].content in res

    form = res.forms[
        'short-text-form-short_text_content_block-content-site-byline']
    new_byline = 'This is a rather mediocre byline.'
    form['content'] = new_byline

    res = form.submit().follow()
    assert new_byline in res
    assert not(default_content['site-byline'].content in res)

    res = testapp.get(url_for('public.logout')).follow()


def test_home_textcontentblock_update_visible_sessionstore(
    app_sessionstore):
    app = app_sessionstore
    with app.test_request_context():
        testapp = TestApp(app)
        user = User.sessionstore_user()

        # Goes to homepage
        res = testapp.get("/")
        # Fills out login form
        form = res.forms['loginForm']
        form['email'] = user.email
        form['password'] = app.config['SESSIONSTORE_USER_PASSWORD']
        # Submits
        res = form.submit().follow()

        default_content = ShortTextContentBlock.default_content()
        assert default_content['site-byline'].content in res

        form = res.forms[
            'short-text-form-short_text_content_block-content-site-byline']
        new_byline = 'This is a rather mediocre byline.'
        form['content'] = new_byline

        res = form.submit().follow()
        assert new_byline in res
        assert not(default_content['site-byline'].content in res)

        res = testapp.get(url_for('public.logout')).follow()


def test_home_event_startdate_update_visible(app, user, testapp):
    # Goes to homepage
    res = testapp.get("/")
    # Fills out login form
    form = res.forms['loginForm']
    form['email'] = user.email
    form['password'] = 'myprecious'
    # Submits
    res = form.submit().follow()

    event = Event.query.filter_by(id=1).one()
    old_start_date_str = event.start_date.strftime('%d %b %Y')
    assert ((
        '<input class="datepicker-enable" '
        'id="event-start_date-1" name="content" '
        'placeholder="Pick your start date" required type="text" '
        'value="{0}">').format(
            old_start_date_str)
        in res)

    form = res.forms[
        'date-pick-form-event-start_date-1']
    new_start_date = (event.start_date + timedelta(days=3))
    new_start_date_str = new_start_date.strftime('%d %b %Y')
    form['content'] = new_start_date_str

    res = form.submit().follow()
    assert ((
        '<input class="datepicker-enable" '
        'id="event-start_date-1" name="content" '
        'placeholder="Pick your start date" required type="text" '
        'value="{0}">').format(
            new_start_date_str)
        in res)

    res = testapp.get(url_for('public.logout')).follow()


def test_home_event_startdate_update_visible_sessionstore(
    app_sessionstore):
    app = app_sessionstore
    with app.test_request_context():
        testapp = TestApp(app)
        user = User.sessionstore_user()

        # Goes to homepage
        res = testapp.get("/")
        # Fills out login form
        form = res.forms['loginForm']
        form['email'] = user.email
        form['password'] = app.config['SESSIONSTORE_USER_PASSWORD']
        # Submits
        res = form.submit().follow()

        event = res.session['event'][1]
        old_start_date = datetime.strptime(
            event['start_date'], '%Y-%m-%d')
        old_start_date_str = (old_start_date
            .strftime('%d %b %Y'))
        assert ((
            '<input class="datepicker-enable" '
            'id="event-start_date-1" name="content" '
            'placeholder="Pick your start date" required type="text" '
            'value="{0}">').format(
                old_start_date_str)
            in res)

        form = res.forms[
            'date-pick-form-event-start_date-1']
        new_start_date = (old_start_date + timedelta(days=3))
        new_start_date_str = new_start_date.strftime('%d %b %Y')
        form['content'] = new_start_date_str

        res = form.submit().follow()
        assert ((
            '<input class="datepicker-enable" '
            'id="event-start_date-1" name="content" '
            'placeholder="Pick your start date" required type="text" '
            'value="{0}">').format(
                new_start_date_str)
            in res)

        res = testapp.get(url_for('public.logout')).follow()


def test_home_event_starttime_update_visible(app, user, testapp):
    # Goes to homepage
    res = testapp.get("/")
    # Fills out login form
    form = res.forms['loginForm']
    form['email'] = user.email
    form['password'] = 'myprecious'
    # Submits
    res = form.submit().follow()

    event = Event.query.filter_by(id=1).one()
    old_start_time_str = (
        event.start_time
        and event.start_time.strftime('%H:%M')
        or '')

    assert ((
        '<input class="timepicker-enable" '
        'id="event-start_time-1" name="content" '
        'placeholder="Pick your start time" type="time" '
        'value="{0}">').format(
            old_start_time_str)
        in res)

    form = res.forms[
        'time-pick-form-event-start_time-1']
    dt_now = datetime.now()
    dt_midnighttoday = datetime(dt_now.year, dt_now.month, dt_now.day)

    rand_delta = timedelta(minutes=(15 * random.randrange(96)))
    new_start_time = (dt_midnighttoday + rand_delta).time()
    new_start_time_str = new_start_time.strftime('%H:%M')

    i = 0
    while i < 3 and new_start_time_str == old_start_time_str:
        rand_delta = timedelta(minutes=(15 * random.randrange(96)))
        new_start_time = (dt_midnighttoday + rand_delta).time()
        new_start_time_str = new_start_time.strftime('%H:%M')

    form['content'] = new_start_time_str

    res = form.submit().follow()
    assert ((
        '<input class="timepicker-enable" '
        'id="event-start_time-1" name="content" '
        'placeholder="Pick your start time" type="time" '
        'value="{0}">').format(
            new_start_time_str)
        in res)

    res = testapp.get(url_for('public.logout')).follow()
