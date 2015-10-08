# -*- coding: utf-8 -*-
from wtforms import TextField, TextAreaField
from wtforms.validators import DataRequired

from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed


class TextEditForm(Form):
    content = TextField('Content', validators=[DataRequired()])


class TextOptionalEditForm(Form):
    content = TextField('Content', validators=[])


class LongTextEditForm(Form):
    content = TextAreaField('Content', validators=[DataRequired()])


class LongTextOptionalEditForm(Form):
    content = TextAreaField('Content', validators=[])


class ImageEditForm(Form):
    image = FileField('Image', validators=[FileAllowed(('gif', 'jpg', 'jpeg', 'png'), 'Only image files (gif, jpg, png) can be uploaded for this field')])
