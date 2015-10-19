# -*- coding: utf-8 -*-
import ast
import os
import pylibmc

os_env = os.environ


class Config(object):
    SECRET_KEY = os_env.get('FLASK_EDITABLESITE_SECRET', 'secret-key')  # TODO: Change me
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))

    SQLALCHEMY_DATABASE_URI = os_env.get(
        'FLASK_EDITABLESITE_DATABASE_URI',
        'postgresql://localhost/example')  # TODO: Change me

    SESSION_TYPE = os_env.get('FLASK_EDITABLESITE_SESSION_TYPE', None)
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'flask-editablesite-session:'
    SESSION_MEMCACHED = (os_env.get('FLASK_EDITABLESITE_SESSION_MEMCACHED', None)
        and pylibmc.Client([os_env.get('FLASK_EDITABLESITE_SESSION_MEMCACHED', None)], binary=True)
        or None)
    SESSION_FILE_DIR = (os_env.get('FLASK_EDITABLESITE_SESSION_FILE_DIR', None)
        and os.path.abspath(os.path.join(APP_DIR, os_env.get('FLASK_EDITABLESITE_SESSION_FILE_DIR', None)))
        or None)

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
        'rich_text_content_block': {
            'classpath': 'flask_editablesite.contentblock.models.RichTextContentBlock',
            'identifier_field': 'slug',
            'title_field': 'title',
            'long_text_fields': ['content'],
        },
        'image_content_block': {
            'classpath': 'flask_editablesite.contentblock.models.ImageContentBlock',
            'identifier_field': 'slug',
            'title_field': 'title',
            'image_fields': ['image'],
            'image_relative_path': 'image-content-block/',
        },
        'gallery_item': {
            'classpath': 'flask_editablesite.gallery.models.GalleryItem',
            'identifier_field': 'id',
            'title_field': 'title',
            'text_fields': ['title', 'date_taken'],
            'long_text_fields': ['content'],
            'image_fields': ['image'],
            'image_relative_path': 'gallery-item/',
            'is_createable': True,
            'is_deleteable': True,
            'is_reorderable': True,
            'weight_field': 'weight',
            'reorder_form_prefix': 'gallery_',
        },
        'event': {
            'classpath': 'flask_editablesite.event.models.Event',
            'identifier_field': 'id',
            'title_field': 'title',
            'text_fields': ['title', 'event_url', 'location_name', 'location_url'],
            'date_fields': ['start_date', 'end_date'],
            'time_fields': ['start_time', 'end_time'],
            'is_createable': True,
            'is_deleteable': True,
        },
    }

    EDITABLE_SAMPLE_IMAGES_SCRAPE_URL = os_env.get('FLASK_EDITABLESITE_EDITABLE_SAMPLE_IMAGES_SCRAPE_URL', None)
    EDITABLE_SAMPLE_IMAGES_SCRAPE_PARENTELNAME = os_env.get('FLASK_EDITABLESITE_EDITABLE_SAMPLE_IMAGES_SCRAPE_PARENTELNAME', None)
    EDITABLE_SAMPLE_IMAGES_SCRAPE_PARENTELCLASS = os_env.get('FLASK_EDITABLESITE_EDITABLE_SAMPLE_IMAGES_SCRAPE_PARENTELCLASS', None)
    EDITABLE_SAMPLE_IMAGES_SCRAPE_ONLYFIRSTEL = (os_env.get('FLASK_EDITABLESITE_EDITABLE_SAMPLE_IMAGES_SCRAPE_ONLYFIRSTEL')
        and ast.literal_eval(os_env.get('FLASK_EDITABLESITE_EDITABLE_SAMPLE_IMAGES_SCRAPE_ONLYFIRSTEL'))
        or False)

    EDITABLE_SAMPLE_IMAGES_RELATIVE_PATH = os_env.get('FLASK_EDITABLESITE_EDITABLE_SAMPLE_IMAGES_RELATIVE_PATH', None)
    EDITABLE_PLACEHOLDER_IMAGE_RELATIVE_PATH = 'placeholder.png'

    EDITABLE_SAMPLE_TEXT_SCRAPE_URLS = (os_env.get('FLASK_EDITABLESITE_EDITABLE_SAMPLE_TEXT_SCRAPE_URLS')
        and ast.literal_eval(os_env.get('FLASK_EDITABLESITE_EDITABLE_SAMPLE_TEXT_SCRAPE_URLS'))
        or [])
    EDITABLE_PLACEHOLDER_TEXT = os_env.get('FLASK_EDITABLESITE_EDITABLE_PLACEHOLDER_TEXT', '<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur enim magna, dignissim sit amet aliquet sed, varius sit amet tellus. Nam elementum, est non dignissim egestas, est turpis ornare nunc, ac ornare nisi purus id orci. Integer blandit sed leo eu tempus. Donec egestas nisl lectus, congue efficitur velit mollis mattis.</p>')

    EDITABLE_SAMPLE_URLS = (os_env.get('FLASK_EDITABLESITE_EDITABLE_SAMPLE_URLS')
        and ast.literal_eval(os_env.get('FLASK_EDITABLESITE_EDITABLE_SAMPLE_URLS'))
        or ['http://google.com/', 'http://facebook.com/', 'http://youtube.com/', 'http://yahoo.com/', 'http://amazon.com/', 'http://wikipedia.org/', 'http://twitter.com/', 'http://live.com/', 'http://linkedin.com/', 'http://ebay.com/', 'http://bing.com/', 'http://instagram.com/'])

    EDITABLE_SAMPLE_IMAGES_CREDITS = os_env.get('FLASK_EDITABLESITE_EDITABLE_SAMPLE_IMAGES_CREDITS', None)
    EDITABLE_SAMPLE_TEXT_CREDITS = os_env.get('FLASK_EDITABLESITE_EDITABLE_SAMPLE_TEXT_CREDITS', None)

    GALLERY_NUM_DEFAULT_ITEMS = (os_env.get('FLASK_EDITABLESITE_GALLERY_NUM_DEFAULT_ITEMS')
        and ast.literal_eval(os_env.get('FLASK_EDITABLESITE_GALLERY_NUM_DEFAULT_ITEMS'))
        or 6)
    GALLERY_LIMIT = (os_env.get('FLASK_EDITABLESITE_GALLERY_LIMIT')
        and ast.literal_eval(os_env.get('FLASK_EDITABLESITE_GALLERY_LIMIT'))
        or 3)

    EVENT_NUM_DEFAULT_ITEMS = (os_env.get('FLASK_EDITABLESITE_EVENT_NUM_DEFAULT_ITEMS')
        and ast.literal_eval(os_env.get('FLASK_EDITABLESITE_EVENT_NUM_DEFAULT_ITEMS'))
        or 12)
    EVENT_UPCOMING_LIMIT = (os_env.get('FLASK_EDITABLESITE_EVENT_UPCOMING_LIMIT')
        and ast.literal_eval(os_env.get('FLASK_EDITABLESITE_EVENT_UPCOMING_LIMIT'))
        or 3)
    EVENT_PAST_LIMIT = (os_env.get('FLASK_EDITABLESITE_EVENT_PAST_LIMIT')
        and ast.literal_eval(os_env.get('FLASK_EDITABLESITE_EVENT_PAST_LIMIT'))
        or 3)


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
