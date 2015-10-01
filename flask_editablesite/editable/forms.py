# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import TextField
from wtforms.validators import DataRequired


class TextEditForm(Form):
    content = TextField('Content', validators=[DataRequired()])
