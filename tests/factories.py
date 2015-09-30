# -*- coding: utf-8 -*-
from factory import Sequence, PostGenerationMethodCall
from factory.alchemy import SQLAlchemyModelFactory

from flask_editablesite.user.models import User
from flask_editablesite.database import db


class BaseFactory(SQLAlchemyModelFactory):

    class Meta:
        abstract = True
        sqlalchemy_session = db.session


class UserFactory(BaseFactory):
    username = Sequence(lambda n: "user{0}".format(n))
    email = Sequence(lambda n: "user{0}@example.com".format(n))
    password = PostGenerationMethodCall('set_password', 'example')
    active = True

    class Meta:
        model = User
