import importlib
import re
from sqlalchemy.exc import IntegrityError

from flask import current_app as app
from flask import (abort, Blueprint, flash, url_for, redirect, request,
                   session, Response)
from flask_login import login_required, current_user

from flask_editablesite.extensions import db
from flask_editablesite.editable.forms import TextEditForm, LongTextEditForm, ImageEditForm


blueprint = Blueprint('editable', __name__, static_folder="../static")


def get_model_class(model_classpath, model_name):
    """Dynamically imports the model with the specified classpath."""

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

    return model_class


def text_update_func(model_name, field_name, model_identifier, is_autosave=False):
    try:
        v = app.config['EDITABLE_MODELS'][model_name]
    except KeyError:
        abort(404)

    if ('long_text_fields' in v) and (field_name in v['long_text_fields']):
        is_long_text = True
    elif ('text_fields' in v) and (field_name in v['text_fields']):
        is_long_text = False
    else:
        abort(404)

    try:
        model_classpath = v['classpath']
    except KeyError:
        raise ValueError('No class path defined in app config\'s EDITABLE_MODELS for model name "%s"' % model_name)

    try:
        identifier_field_name = v['identifier_field']
    except KeyError:
        raise ValueError('No identifier field defined in app config\'s EDITABLE_MODELS for model name "%s"' %  model_name)

    try:
        title_field_name = v['title_field']
    except KeyError:
        raise ValueError('No title field defined in app config\'s EDITABLE_MODELS for model name "%s"' %  model_name)

    model_class = get_model_class(model_classpath, model_name)

    filter_by_kwargs = {
        identifier_field_name: model_identifier,
        'active': True}
    model = None

    if app.config.get('USE_SESSIONSTORE_NOT_DB'):
        model_dict = (session.get(model_name, {})
            .get(model_identifier, None))

        if model_dict:
            model = model_class(**model_dict)
    else:
        model = (model_class.query
            .filter_by(**filter_by_kwargs)
            .first())

    if not model:
        try:
            model = model_class.default_content()[model_identifier]
        except KeyError:
            abort(404)

    form = is_long_text and LongTextEditForm() or TextEditForm()

    if form.validate_on_submit():
        content = form.content.data

        try:
            if app.config.get('USE_SESSIONSTORE_NOT_DB'):
                if session.get(model_name) == None:
                    session[model_name] = {}

                if not (session.get(model_name, {})
                        .get(model_identifier, None)):
                    session[model_name][model_identifier] = {
                        title_field_name: getattr(model, title_field_name)}

                session[model_name][model_identifier][field_name] = content
            else:
                setattr(model, field_name, content)
                model.save()

            app.logger.info('{0} updated: {1}; user: {2}'.format(model_name.replace('_', ' ').capitalize(), model, current_user))

            if is_autosave:
                return Response('OK')
            else:
                flash("{0} has been updated.".format(getattr(model, title_field_name)), 'success')
        except IntegrityError as e:
            db.session.rollback()

            if is_autosave:
                return Response('ERROR', 400)
            else:
                flash("Error updating {0}.".format(getattr(model, title_field_name)), 'danger')
    else:
        if is_autosave:
            return Response('ERROR', 400)
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


def image_update_func(model_name, field_name, model_identifier, is_dropzone=False):
    try:
        v = app.config['EDITABLE_MODELS'][model_name]
    except KeyError:
        abort(404)

    if not(('image_fields' in v) and (field_name in v['image_fields'])):
        abort(404)

    try:
        model_classpath = v['classpath']
    except KeyError:
        raise ValueError('No class path defined in app config\'s EDITABLE_MODELS for model name "%s"' % model_name)

    try:
        identifier_field_name = v['identifier_field']
    except KeyError:
        raise ValueError('No identifier field defined in app config\'s EDITABLE_MODELS for model name "%s"' %  model_name)

    try:
        title_field_name = v['title_field']
    except KeyError:
        raise ValueError('No title field defined in app config\'s EDITABLE_MODELS for model name "%s"' %  model_name)

    model_class = get_model_class(model_classpath, model_name)

    filter_by_kwargs = {
        identifier_field_name: model_identifier,
        'active': True}
    model = None

    if app.config.get('USE_SESSIONSTORE_NOT_DB'):
        model_dict = (session.get(model_name, {})
            .get(model_identifier, None))

        if model_dict:
            model = model_class(**model_dict)
    else:
        model = (model_class.query
            .filter_by(**filter_by_kwargs)
            .first())

    if not model:
        try:
            model = model_class.default_content()[model_identifier]
        except KeyError:
            abort(404)

    if request.files:
        request.form = request.form.copy()
        request.form.update(request.files)

    form = ImageEditForm()

    if form.validate_on_submit():
        image_orig = getattr(model, field_name)

        filehandle = form.image.data
        parts = os.path.splitext(filehandle.filename)


@blueprint.route("/image-update/<model_name>/<field_name>/<model_identifier>/", methods=["POST"])
@login_required
def image_update(model_name, field_name, model_identifier):
    return image_update_func(
        model_name=model_name,
        field_name=field_name,
        model_identifier=model_identifier)


@blueprint.route("/image-update-dropzone/<model_name>/<field_name>/<model_identifier>/", methods=["POST"])
@login_required
def image_update_dropzone(model_name, field_name, model_identifier):
    return image_update_func(
        model_name=model_name,
        field_name=field_name,
        model_identifier=model_identifier,
        is_dropzone=True)
