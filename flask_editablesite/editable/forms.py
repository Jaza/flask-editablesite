# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import TextField, TextAreaField
from wtforms.validators import DataRequired


class TextEditForm(Form):
    content = TextField('Content', validators=[DataRequired()])


class LongTextEditForm(Form):
    content = TextAreaField('Content', validators=[DataRequired()])
