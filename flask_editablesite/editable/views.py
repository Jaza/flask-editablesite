from datetime import datetime
from glob import glob
import os
from sqlalchemy.exc import IntegrityError

from flask import current_app as app
from flask import (abort, Blueprint, flash, url_for, redirect, request,
                   session, Response)
from flask_login import login_required, current_user
from flask_transfer import Transfer
from werkzeug import secure_filename

from flask_editablesite.extensions import db
from flask_editablesite.editable.forms import TextEditForm, LongTextEditForm, ImageEditForm
from flask_editablesite.editable.utils import get_model_class
from flask_editablesite.editable.sample_images import placeholder_or_random_sample_image


blueprint = Blueprint('editable', __name__, static_folder="../static")


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

    try:
        image_relative_path = v['image_relative_path']
    except KeyError:
        raise ValueError('No image relative path defined in app config\'s EDITABLE_MODELS for model name "%s"' %  model_name)

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
        if app.config.get('USE_SESSIONSTORE_NOT_DB'):
            image = placeholder_or_random_sample_image()
        else:
            image_orig = getattr(model, field_name)

            filehandle = form.image.data
            parts = os.path.splitext(filehandle.filename)

            filename = '%s%s/%s' % (
                image_relative_path,
                getattr(model, identifier_field_name),
                secure_filename('%s-%s%s' % (parts[0], datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S'), parts[1])))

            filepath = os.path.abspath(
                os.path.join(
                    app.config['MEDIA_FOLDER'],
                    filename))

            if not os.path.exists(os.path.dirname(filepath)):
                os.makedirs(os.path.dirname(filepath))

            Transfer().save(filehandle, destination=filepath)

            image = filename

        try:
            if app.config.get('USE_SESSIONSTORE_NOT_DB'):
                if session.get(model_name) == None:
                    session[model_name] = {}

                if not (session.get(model_name, {})
                        .get(model_identifier, None)):
                    session[model_name][model_identifier] = {
                        title_field_name: getattr(model, title_field_name)}

                session[model_name][model_identifier][field_name] = image
            else:
                setattr(model, field_name, image)
                model.save()

                if (image_orig and
                        (image_orig != app.config['EDITABLE_PLACEHOLDER_IMAGE_RELATIVE_PATH'])):
                    filepath = os.path.abspath(
                        os.path.join(app.config['MEDIA_FOLDER'],
                        image_orig))

                    if os.path.exists(filepath):
                        os.remove(filepath)

                    glob_filepath_split = os.path.splitext(
                        os.path.join(
                            app.config['MEDIA_THUMBNAIL_FOLDER'],
                            image_orig))
                    glob_filepath = glob_filepath_split[0]
                    glob_matches = glob('%s*' % glob_filepath)

                    for fp in glob_matches:
                        if os.path.exists(fp):
                            os.remove(fp)

            app.logger.info('{0} updated: {1}; user: {2}'.format(model_name.replace('_', ' ').capitalize(), model, current_user))

            if is_dropzone:
                return Response('OK')
            else:
                flash("{0} has been updated.".format(getattr(model, title_field_name)), 'success')
        except IntegrityError as e:
            db.session.rollback()

            if is_dropzone:
                return Response('ERROR')
            else:
                flash("Error updating {0}.".format(getattr(model, title_field_name)), 'danger')
    else:
        if is_dropzone:
            return Response('ERROR')
        else:
            flash_errors(form)

    return redirect(url_for("public.home"))


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
