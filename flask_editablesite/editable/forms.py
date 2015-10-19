# -*- coding: utf-8 -*-
from wtforms import TextField, TextAreaField, HiddenField, FieldList, FormField, DateField
from wtforms_components import TimeField
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
    image = FileField('Image', validators=[DataRequired(), FileAllowed(('gif', 'jpg', 'jpeg', 'png'), 'Only image files (gif, jpg, png) can be uploaded for this field')])


class ImageOptionalEditForm(Form):
    image = FileField('Image', validators=[FileAllowed(('gif', 'jpg', 'jpeg', 'png'), 'Only image files (gif, jpg, png) can be uploaded for this field')])


class DateEditForm(Form):
    content = DateField('Date', format='%d %b %Y', validators=[DataRequired()])


class DateOptionalEditForm(Form):
    content = DateField('Date', format='%d %b %Y', validators=[])


class TimeEditForm(Form):
    content = TimeField('Time', validators=[DataRequired()])


class TimeOptionalEditForm(Form):
    content = TimeField('Time', validators=[])


class ReorderItemForm(Form):
    identifier = HiddenField(validators=[])
    weight = HiddenField(validators=[])


class ReorderForm(Form):
    items = FieldList(FormField(ReorderItemForm))
