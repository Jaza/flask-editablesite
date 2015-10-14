# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
import os

from flask import Flask, render_template

from flask_editablesite.settings import ProdConfig
from flask_editablesite.assets import assets
from flask_editablesite.extensions import (
    bcrypt,
    cache,
    db,
    login_manager,
    mail,
    sess,
    migrate,
    debug_toolbar,
    thumb,
)
from flask_editablesite import public, editable


def create_app(config_object=ProdConfig):
    """An application factory, as explained here:
        http://flask.pocoo.org/docs/patterns/appfactories/

    :param config_object: The configuration object to use.
    """
    app = Flask(__name__)
    app.config.from_object(config_object)
    register_loggers(app)
    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    return app


def register_extensions(app):
    assets.init_app(app)
    bcrypt.init_app(app)
    cache.init_app(app)
    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    debug_toolbar.init_app(app)
    migrate.init_app(app, db)
    thumb.init_app(app)

    if app.config.get('SESSION_TYPE'):
        sess.init_app(app)

    return None


def register_blueprints(app):
    app.register_blueprint(public.views.blueprint)
    app.register_blueprint(editable.views.blueprint)
    return None


def register_errorhandlers(app):
    def render_error(error):
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, 'code', 500)
        return render_template("{0}.html".format(error_code)), error_code
    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None


def register_loggers(app):
    import logging

    log_formatter = logging.Formatter('%(levelname)s %(asctime)s %(message)s', '[%Y-%m-%d %H:%M:%S]')

    if len(app.logger.handlers):
        app.logger.handlers[0].setFormatter(log_formatter)

    if not app.debug:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(log_formatter)
        app.logger.addHandler(stream_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('flask_editablesite startup')
