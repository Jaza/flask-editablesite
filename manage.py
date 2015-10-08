#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from flask_script import Manager, Shell, Server
from flask_script.commands import Clean, ShowUrls
from flask_migrate import MigrateCommand

from flask_editablesite.app import create_app
from flask_editablesite.user.commands import CreateUser
from flask_editablesite.editable.commands import DownloadSampleImages
from flask_editablesite.user.models import User
from flask_editablesite.settings import DevConfig, ProdConfig
from flask_editablesite.database import db

if os.environ.get("FLASK_EDITABLESITE_ENV") == 'prod':
    app = create_app(ProdConfig)
else:
    app = create_app(DevConfig)

HERE = os.path.abspath(os.path.dirname(__file__))
TEST_PATH = os.path.join(HERE, 'tests')

manager = Manager(app)


def _make_context():
    """Return context dict for a shell session so you can access
    app, db, and the User model by default.
    """
    return {'app': app, 'db': db, 'User': User}


@manager.command
def test():
    """Run the tests."""
    import pytest
    exit_code = pytest.main([TEST_PATH, '--verbose'])
    return exit_code


manager.add_command('server', Server())
manager.add_command('shell', Shell(make_context=_make_context))
manager.add_command('db', MigrateCommand)
manager.add_command("urls", ShowUrls())
manager.add_command("clean", Clean())
manager.add_command("createuser", CreateUser())
manager.add_command("downloadsampleimages", DownloadSampleImages())

if __name__ == '__main__':
    manager.run()
