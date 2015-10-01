# -*- coding: utf-8 -*-
import ast
import os

os_env = os.environ


class Config(object):
    SECRET_KEY = os_env.get('FLASK_EDITABLESITE_SECRET', 'secret-key')  # TODO: Change me
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))

    SQLALCHEMY_DATABASE_URI = os_env.get(
        'FLASK_EDITABLESITE_DATABASE_URI',
        'postgresql://localhost/example')  # TODO: Change me

    USE_SESSIONSTORE_NOT_DB = (os_env.get('FLASK_EDITABLESITE_USE_SESSIONSTORE_NOT_DB')
        and ast.literal_eval(os_env.get('FLASK_EDITABLESITE_USE_SESSIONSTORE_NOT_DB'))
        or False)

    SESSIONSTORE_USER_EMAIL = os_env.get(
        'FLASK_EDITABLESITE_SESSIONSTORE_USER_EMAIL',
        'test@test.com')
    SESSIONSTORE_USER_FIRST_NAME = os_env.get(
        'FLASK_EDITABLESITE_SESSIONSTORE_USER_FIRST_NAME',
        'Test')
    SESSIONSTORE_USER_LAST_NAME = os_env.get(
        'FLASK_EDITABLESITE_SESSIONSTORE_USER_LAST_NAME',
        'Dude')
    SESSIONSTORE_USER_PASSWORD = os_env.get(
        'FLASK_EDITABLESITE_SESSIONSTORE_USER_PASSWORD',
        'test')

    BCRYPT_LOG_ROUNDS = 13
    ASSETS_DEBUG = False
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.

    SITE_NAME = 'Flask Editable Site'

    ADMINS = (os_env.get('FLASK_EDITABLESITE_ADMINS')
        and os_env.get('FLASK_EDITABLESITE_ADMINS').split(',')
        or ['sitedevdude@nonexistentemailaddress.com'])

    MAIL_DEFAULT_SENDER = os_env.get('FLASK_EDITABLESITE_MAIL_DEFAULT_SENDER', 'sender@nonexistentemailaddress.com')
    CONTACT_EMAIL_RECIPIENTS = (os_env.get('FLASK_EDITABLESITE_CONTACT_EMAIL_RECIPIENTS')
        and os_env.get('FLASK_EDITABLESITE_CONTACT_EMAIL_RECIPIENTS').split(',')
        or ['recipient@nonexistentemailaddress.com'])

    MAIL_SERVER = os_env.get('FLASK_EDITABLESITE_MAIL_SERVER', 'localhost')
    MAIL_PORT = (os_env.get('FLASK_EDITABLESITE_MAIL_PORT')
        and ast.literal_eval(os_env.get('FLASK_EDITABLESITE_MAIL_PORT'))
        or 25)
    MAIL_USE_TLS = (os_env.get('FLASK_EDITABLESITE_MAIL_USE_TLS')
        and ast.literal_eval(os_env.get('FLASK_EDITABLESITE_MAIL_USE_TLS'))
        or False)
    MAIL_USE_SSL = (os_env.get('FLASK_EDITABLESITE_MAIL_USE_SSL')
        and ast.literal_eval(os_env.get('FLASK_EDITABLESITE_MAIL_USE_SSL'))
        or False)
    MAIL_USERNAME = os_env.get('FLASK_EDITABLESITE_MAIL_USERNAME', None)
    MAIL_PASSWORD = os_env.get('FLASK_EDITABLESITE_MAIL_PASSWORD', None)

    GOOGLE_ANALYTICS_ACCOUNT_ID = os_env.get('FLASK_EDITABLESITE_GOOGLE_ANALYTICS_ACCOUNT_ID', None)

    SESSION_COOKIE_NAME = 'flask_editablesite_session'
    REMEMBER_COOKIE_NAME = 'flask_editablesite_remember_token'

    UPLOADS_RELATIVE_PATH = 'uploads/'
    MEDIA_FOLDER = os.path.abspath(os.path.join(APP_DIR, 'static/uploads'))
    MEDIA_URL = '/static/uploads/'
    MEDIA_THUMBNAIL_FOLDER = os.path.abspath(os.path.join(APP_DIR, 'static/cache/thumbnails'))
    MEDIA_THUMBNAIL_URL = 'cache/thumbnails/'

    ERROR_MAIL_FORMAT = (
        '\n'
        'Message type:       %(levelname)s\n'
        'Location:           %(pathname)s:%(lineno)d\n'
        'Module:             %(module)s\n'
        'Function:           %(funcName)s\n'
        'Time:               %(asctime)s\n'
        '\n'
        'Message:\n'
        '\n'
        '%(message)s\n')

    EDITABLE_MODELS = {
        'short_text_content_block': {
            'classpath': 'flask_editablesite.contentblock.models.ShortTextContentBlock',
            'identifier_field': 'slug',
            'title_field': 'title',
            'text_fields': ['content'],
        },
    }


class ProdConfig(Config):
    """Production configuration."""
    ENV = 'prod'
    DEBUG = False
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar


class DevConfig(Config):
    """Development configuration."""
    ENV = 'dev'
    DEBUG = True
    DEBUG_TB_ENABLED = True
    ASSETS_DEBUG = True  # Don't bundle/minify static assets
    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.


class TestConfig(Config):
    TESTING = True
    DEBUG = True
    BCRYPT_LOG_ROUNDS = 1  # For faster tests
    WTF_CSRF_ENABLED = False  # Allows form testing
