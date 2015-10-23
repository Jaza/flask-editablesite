# -*- coding: utf-8 -*-
"""Test editable view routes."""

from datetime import datetime, timedelta
import os
import random
import string
from webtest import Upload
from flask_webtest import TestApp

from flask import url_for

from flask_editablesite.extensions import thumb
from flask_editablesite.contentblock.models import (
    ShortTextContentBlock, ImageContentBlock)
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


def test_home_imagecontentblock_update_visible(app, user, testapp):
    # Goes to homepage
    res = testapp.get("/")
    # Fills out login form
    form = res.forms['loginForm']
    form['email'] = user.email
    form['password'] = 'myprecious'
    # Submits
    res = form.submit().follow()

    assert (
        (
            '<img class="img-responsive img-circle img-lesswidth" '
            'src="{0}" alt="{1}">').format(
                url_for('static', filename=thumb.thumbnail(
                    app.config[
                        'EDITABLE_PLACEHOLDER_IMAGE_RELATIVE_PATH'],
                    size='256x256',
                    crop='fit')),
                app.config['SITE_NAME'])
        in res.text)

    form = res.forms[
        'image-form-image_content_block-image-site-logo']

    old_image_filepath = '{0}/{1}'.format(
        app.config['MEDIA_FOLDER'],
        app.config['EDITABLE_PLACEHOLDER_IMAGE_RELATIVE_PATH'])
    assert os.path.exists(old_image_filepath)
    old_image_file = open(old_image_filepath, 'rb')

    new_image_filename = ''.join(
        random.choice(string.ascii_lowercase) for _ in range(10))
    new_image_filename += '.jpg'

    form['image'] = Upload(
        new_image_filename,
        old_image_file.read(),
        'image/jpeg')
    old_image_file.close()

    res = form.submit().follow()

    icb = (
        ImageContentBlock.query
                         .filter_by(slug='site-logo')
                         .one())

    new_image_filepath = '{0}/{1}'.format(
        app.config['MEDIA_FOLDER'],
        icb.image)
    assert os.path.exists(new_image_filepath)

    assert (
        (
            '<img class="img-responsive img-circle img-lesswidth" '
            'src="{0}" alt="{1}">').format(
                url_for('static', filename=thumb.thumbnail(
                    icb.image,
                    size='256x256',
                    crop='fit')),
                app.config['SITE_NAME'])
        in res.text)

    os.remove(new_image_filepath)

    res = testapp.get(url_for('public.logout')).follow()


def test_home_imagecontentblock_update_visible_sessionstore(
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

        assert (
            (
                '<img class="img-responsive img-circle img-lesswidth" '
                'src="{0}" alt="{1}">').format(
                    url_for('static', filename=thumb.thumbnail(
                        app.config[
                            'EDITABLE_PLACEHOLDER_IMAGE_RELATIVE_PATH'],
                        size='256x256',
                        crop='fit')),
                    app.config['SITE_NAME'])
            in res.text)

        form = res.forms[
            'image-form-image_content_block-image-site-logo']

        old_image_filepath = '{0}/{1}'.format(
            app.config['MEDIA_FOLDER'],
            app.config['EDITABLE_PLACEHOLDER_IMAGE_RELATIVE_PATH'])
        assert os.path.exists(old_image_filepath)
        old_image_file = open(old_image_filepath, 'rb')

        new_image_filename = ''.join(
            random.choice(string.ascii_lowercase) for _ in range(10))
        new_image_filename += '.jpg'

        form['image'] = Upload(
            new_image_filename,
            old_image_file.read(),
            'image/jpeg')
        old_image_file.close()

        res = form.submit().follow()

        assert (
            (
                '<img class="img-responsive img-circle img-lesswidth" '
                'src="{0}" alt="{1}">').format(
                    url_for('static', filename=thumb.thumbnail(
                        app.config[
                            'EDITABLE_PLACEHOLDER_IMAGE_RELATIVE_PATH'],
                        size='256x256',
                        crop='fit')),
                    app.config['SITE_NAME'])
            in res.text)

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
        old_start_date_str = old_start_date.strftime('%d %b %Y')
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


def test_home_event_starttime_update_visible_sessionstore(
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
        dt_now_str = datetime.now().strftime('%Y-%m-%d')
        old_start_time_str = ''

        if (('start_time') in event) and event['start_time']:
            old_start_time = (
                datetime.strptime(
                    dt_now_str + ' ' + event['start_time'],
                    '%Y-%m-%d %H:%M:%S')
                .time())
            old_start_time_str = old_start_time.strftime('%H:%M')

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


def test_home_event_add_visible(app, user, testapp):
    # Goes to homepage
    res = testapp.get("/")
    # Fills out login form
    form = res.forms['loginForm']
    form['email'] = user.email
    form['password'] = 'myprecious'
    # Submits
    res = form.submit().follow()

    assert Event.query.count() == app.config['EVENT_NUM_DEFAULT_ITEMS']
    assert (
        len(
            res.html.findAll('article', {'class': 'events-item'}))
        == app.config['EVENT_NUM_DEFAULT_ITEMS'])

    form = res.forms['event-add']

    res = form.submit().follow()
    assert (
        Event.query.count() == (
            app.config['EVENT_NUM_DEFAULT_ITEMS'] + 1))
    assert (
        len(
            res.html.findAll('article', {'class': 'events-item'}))
        == (app.config['EVENT_NUM_DEFAULT_ITEMS'] + 1))

    event = Event.query.order_by(Event.id.desc()).first()
    event.delete()

    res = testapp.get(url_for('public.logout')).follow()


def test_home_event_add_visible_sessionstore(app_sessionstore):
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

        assert (len(res.session['event']) - 1) == app.config[
            'EVENT_NUM_DEFAULT_ITEMS']
        assert (
            len(
                res.html.findAll('article', {'class': 'events-item'}))
            == app.config['EVENT_NUM_DEFAULT_ITEMS'])

        form = res.forms['event-add']

        res = form.submit().follow()
        assert (
            (len(res.session['event']) - 1) == (
                app.config['EVENT_NUM_DEFAULT_ITEMS'] + 1))
        assert (
            len(
                res.html.findAll('article', {'class': 'events-item'}))
            == (app.config['EVENT_NUM_DEFAULT_ITEMS'] + 1))

        res.session['event'].pop()

        res = testapp.get(url_for('public.logout')).follow()


def test_home_event_delete_visible(app, user, testapp):
    # Goes to homepage
    res = testapp.get("/")
    # Fills out login form
    form = res.forms['loginForm']
    form['email'] = user.email
    form['password'] = 'myprecious'
    # Submits
    res = form.submit().follow()

    assert Event.query.count() == app.config['EVENT_NUM_DEFAULT_ITEMS']
    assert (
        len(
            res.html.findAll('article', {'class': 'events-item'}))
        == app.config['EVENT_NUM_DEFAULT_ITEMS'])

    form = res.forms['event-delete-1']

    res = form.submit().follow()
    assert (
        Event.query.count() == (
            app.config['EVENT_NUM_DEFAULT_ITEMS'] - 1))
    assert (
        len(
            res.html.findAll('article', {'class': 'events-item'}))
        == (app.config['EVENT_NUM_DEFAULT_ITEMS'] - 1))

    form = res.forms['event-add']
    res = form.submit().follow()

    res = testapp.get(url_for('public.logout')).follow()


def test_home_event_delete_visible_sessionstore(app_sessionstore):
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

        assert (
            (len(res.session['event']) - 1)
            == app.config['EVENT_NUM_DEFAULT_ITEMS'])
        assert (
            len(
                res.html.findAll('article', {'class': 'events-item'}))
            == app.config['EVENT_NUM_DEFAULT_ITEMS'])

        form = res.forms['event-delete-1']

        res = form.submit().follow()
        assert (
            (len(res.session['event']) - 1) == (
                app.config['EVENT_NUM_DEFAULT_ITEMS'] - 1))
        assert (
            len(
                res.html.findAll('article', {'class': 'events-item'}))
            == (app.config['EVENT_NUM_DEFAULT_ITEMS'] - 1))

        form = res.forms['event-add']
        res = form.submit().follow()

        res = testapp.get(url_for('public.logout')).follow()


def test_home_gallery_reorder_visible(app, user, testapp):
    # Goes to homepage
    res = testapp.get("/")
    # Fills out login form
    form = res.forms['loginForm']
    form['email'] = user.email
    form['password'] = 'myprecious'
    # Submits
    res = form.submit().follow()

    form = res.forms['gi-reorder']
    assert form['gallery_items-0-identifier'].value == '1'
    assert form['gallery_items-0-weight'].value == '0'
    assert form['gallery_items-1-identifier'].value == '2'
    assert form['gallery_items-1-weight'].value == '1'

    form['gallery_items-0-weight'] = '1'
    form['gallery_items-1-weight'] = '0'

    res = form.submit().follow()

    form = res.forms['gi-reorder']
    assert form['gallery_items-0-identifier'].value == '2'
    assert form['gallery_items-0-weight'].value == '0'
    assert form['gallery_items-1-identifier'].value == '1'
    assert form['gallery_items-1-weight'].value == '1'


def test_home_gallery_reorder_visible_sessionstore(app_sessionstore):
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

        form = res.forms['gi-reorder']
        assert form['gallery_items-0-identifier'].value == '1'
        assert form['gallery_items-0-weight'].value == '0'
        assert form['gallery_items-1-identifier'].value == '2'
        assert form['gallery_items-1-weight'].value == '1'

        form['gallery_items-0-weight'] = '1'
        form['gallery_items-1-weight'] = '0'

        res = form.submit().follow()

        form = res.forms['gi-reorder']
        assert form['gallery_items-0-identifier'].value == '1'
        assert form['gallery_items-0-weight'].value == '0'
        assert form['gallery_items-1-identifier'].value == '2'
        assert form['gallery_items-1-weight'].value == '1'
