# -*- coding: utf-8 -*-
from flask import current_app as app
from flask_wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import DataRequired

from flask_editablesite.user.models import User


class LoginForm(Form):
    email = TextField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        initial_validation = super(LoginForm, self).validate()
        if not initial_validation:
            return False

        # Log in with dummy credentials when we're set to 'sessionstore'
        # instead of 'db'.
        if app.config.get('USE_SESSIONSTORE_NOT_DB'):
            if self.email.data != app.config['SESSIONSTORE_USER_EMAIL']:
                self.email.errors.append('Unknown email')
                return False

            if self.password.data != app.config['SESSIONSTORE_USER_PASSWORD']:
                self.password.errors.append('Invalid password')
                return False

            self.user = User.sessionstore_user()
        # Regular login.
        else:
            self.user = User.query.filter_by(email=self.email.data).first()
            if not self.user:
                self.email.errors.append('Unknown email')
                return False

            if not self.user.check_password(self.password.data):
                self.password.errors.append('Invalid password')
                return False

            if not self.user.active:
                self.email.errors.append('User {0} not activated'.format(
                    self.user.full_name_or_email))
                return False

        return True
