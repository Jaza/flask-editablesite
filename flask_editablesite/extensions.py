# -*- coding: utf-8 -*-
"""Extensions module. Each extension is initialized in the app factory located
in app.py
"""

from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cache import Cache
from flask_mail import Mail
from flask_session import Session
from flask_debugtoolbar import DebugToolbarExtension
from flask_thumbnails import Thumbnail

bcrypt = Bcrypt()
login_manager = LoginManager()
db = SQLAlchemy()
migrate = Migrate()
cache = Cache()
mail = Mail()
sess = Session()
debug_toolbar = DebugToolbarExtension()
thumb = Thumbnail()
