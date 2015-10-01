import importlib
import re
from sqlalchemy.exc import IntegrityError

from flask import current_app as app
from flask import (abort, Blueprint, flash, url_for, redirect, request,
                   Response)
from flask_login import login_required, current_user

from flask_editablesite.extensions import db
from flask_editablesite.editable.forms import TextEditForm


blueprint = Blueprint('editable', __name__, static_folder="../static")


def text_update_func(model_name, field_name, model_identifier, is_autosave=False):
    try:
        model_classpath = app.config['EDITABLE_MODELS'][model_name]['classpath']
    except KeyError:
        raise ValueError('No class path defined in app config\'s EDITABLE_MODELS for model name "%s"' % model_name)

    if not('text_fields' in app.config['EDITABLE_MODELS'][model_name]) or not(field_name in app.config['EDITABLE_MODELS'][model_name]['text_fields']):
        raise ValueError('No text field "%s" defined in app config\'s EDITABLE_MODELS for model name "%s"' % (field_name, model_name))

    try:
        identifier_field_name = app.config['EDITABLE_MODELS'][model_name]['identifier_field']
    except KeyError:
        raise ValueError('No identifier field defined in app config\'s EDITABLE_MODELS for model name "%s"' %  model_name)

    try:
        title_field_name = app.config['EDITABLE_MODELS'][model_name]['title_field']
    except KeyError:
        raise ValueError('No title field defined in app config\'s EDITABLE_MODELS for model name "%s"' %  model_name)

    model_classpath_format = r'^[a-z0-9_]+(\.[A-Za-z0-9_]+)+$'
    if not re.match(model_classpath_format, model_classpath):
        raise ValueError('Class path "%s" for model name "%s" must be a valid Python module / class path (in the format "%s")' % (model_classpath, model_name, model_classpath_format))

    model_classpath_split = model_classpath.rpartition('.')
    model_modulepath, model_classname = (model_classpath_split[0], model_classpath_split[2])

    try:
        model_module = importlib.import_module(model_modulepath)
    except ImportError:
        raise ValueError('Error importing module "%s" for model name "%s"' % (model_modulepath, model_name))

    model_class = getattr(model_module, model_classname, None)
    if not model_class:
        raise ValueError('Class "%s" not found in module "%s" for model name "%s"' % (model_classname, model_modulepath, model_name))

    filter_by_kwargs = {
        identifier_field_name: model_identifier,
        'active': True}

    model = (model_class.query
        .filter_by(**filter_by_kwargs)
        .first())

    if not model:
        try:
            model = model_class.default_content()[model_identifier]
        except KeyError:
            abort(404)

    form = TextEditForm()

    if form.validate_on_submit():
        content = form.content.data
        setattr(model, field_name, content)

        try:
            model.save()
            app.logger.info('{0} updated: {1}; user: {2}'.format(model_name.replace('_', ' ').capitalize(), model, current_user))

            if is_autosave:
                return Response('OK')
            else:
                flash("{0} has been updated.".format(getattr(model, title_field_name)), 'success')
        except IntegrityError as e:
            db.session.rollback()

            if is_autosave:
                return Response('ERROR')
            else:
                flash("Error updating {0}.".format(getattr(model, title_field_name)), 'danger')
    else:
        if is_autosave:
            return Response('ERROR')
        else:
            flash_errors(form)

    return redirect(url_for("public.home"))


@blueprint.route("/text-update/<model_name>/<field_name>/<model_identifier>/", methods=["POST"])
@login_required
def text_update(model_name, field_name, model_identifier):
    return text_update_func(
        model_name=model_name,
        field_name=field_name,
        model_identifier=model_identifier)


@blueprint.route("/text-update-autosave/<model_name>/<field_name>/<model_identifier>/", methods=["POST"])
@login_required
def text_update_autosave(model_name, field_name, model_identifier):
    return text_update_func(
        model_name=model_name,
        field_name=field_name,
        model_identifier=model_identifier,
        is_autosave=True)
