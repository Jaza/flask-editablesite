from datetime import datetime
from glob import glob
from operator import itemgetter
import os
from sqlalchemy.exc import IntegrityError

from flask import current_app as app
from flask import (abort, Blueprint, flash, url_for, redirect, request,
                   session, Response)
from flask_login import login_required, current_user
from flask_transfer import Transfer
from werkzeug import secure_filename
from flask_wtf import Form

from flask_editablesite.extensions import db
from flask_editablesite.editable.forms import TextEditForm, LongTextEditForm, DateEditForm, TimeEditForm, ImageEditForm, ReorderForm
from flask_editablesite.editable.utils import get_model_class
from flask_editablesite.editable.sample_images import placeholder_or_random_sample_image
from flask_editablesite.editable.sample_text import placeholder_or_random_sample_text
from flask_editablesite.utils import flash_errors


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

    try:
        model_identifier_int = int(model_identifier)
    except ValueError:
        model_identifier_int = None

    filter_by_kwargs = {
        identifier_field_name: model_identifier,
        'active': True}
    model = None

    if app.config.get('USE_SESSIONSTORE_NOT_DB'):
        model_store = session.get(model_name, None)
        model_dict = None

        if model_store and (type(model_store).__name__ == 'list'):
            try:
                model_dict = model_store[model_identifier_int]
            except KeyError:
                pass
        elif model_store and (type(model_store).__name__ == 'dict'):
            model_dict = model_store.get(model_identifier, None)

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

                if not model_identifier_int:
                    if not (session.get(model_name, {})
                            .get(model_identifier, None)):
                        session[model_name][model_identifier] = {
                            title_field_name: getattr(model, title_field_name)}

                session[model_name][(model_identifier_int or model_identifier)][field_name] = content
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


def date_update_func(model_name, field_name, model_identifier, is_autosave=False):
    try:
        v = app.config['EDITABLE_MODELS'][model_name]
    except KeyError:
        abort(404)

    if not(('date_fields' in v) and (field_name in v['date_fields'])):
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

    try:
        model_identifier_int = int(model_identifier)
    except ValueError:
        model_identifier_int = None

    filter_by_kwargs = {
        identifier_field_name: model_identifier,
        'active': True}
    model = None

    if app.config.get('USE_SESSIONSTORE_NOT_DB'):
        model_store = session.get(model_name, None)
        model_dict = None

        if model_store and (type(model_store).__name__ == 'list'):
            try:
                model_dict = model_store[model_identifier_int]
            except KeyError:
                pass
        elif model_store and (type(model_store).__name__ == 'dict'):
            model_dict = model_store.get(model_identifier, None)

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

    form = DateEditForm()

    if form.validate_on_submit():
        content = form.content.data

        try:
            if app.config.get('USE_SESSIONSTORE_NOT_DB'):
                if session.get(model_name) == None:
                    session[model_name] = {}

                if not model_identifier_int:
                    if not (session.get(model_name, {})
                            .get(model_identifier, None)):
                        session[model_name][model_identifier] = {
                            title_field_name: getattr(model, title_field_name)}

                session[model_name][(model_identifier_int or model_identifier)][field_name] = content.strftime('%Y-%m-%d')
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


@blueprint.route("/date-update/<model_name>/<field_name>/<model_identifier>/", methods=["POST"])
@login_required
def date_update(model_name, field_name, model_identifier):
    return date_update_func(
        model_name=model_name,
        field_name=field_name,
        model_identifier=model_identifier)


@blueprint.route("/date-update-autosave/<model_name>/<field_name>/<model_identifier>/", methods=["POST"])
@login_required
def date_update_autosave(model_name, field_name, model_identifier):
    return date_update_func(
        model_name=model_name,
        field_name=field_name,
        model_identifier=model_identifier,
        is_autosave=True)


def time_update_func(model_name, field_name, model_identifier, is_autosave=False):
    try:
        v = app.config['EDITABLE_MODELS'][model_name]
    except KeyError:
        abort(404)

    if not(('time_fields' in v) and (field_name in v['time_fields'])):
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

    try:
        model_identifier_int = int(model_identifier)
    except ValueError:
        model_identifier_int = None

    filter_by_kwargs = {
        identifier_field_name: model_identifier,
        'active': True}
    model = None

    if app.config.get('USE_SESSIONSTORE_NOT_DB'):
        model_store = session.get(model_name, None)
        model_dict = None

        if model_store and (type(model_store).__name__ == 'list'):
            try:
                model_dict = model_store[model_identifier_int]
            except KeyError:
                pass
        elif model_store and (type(model_store).__name__ == 'dict'):
            model_dict = model_store.get(model_identifier, None)

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

    form = TimeEditForm()

    if form.validate_on_submit():
        content = form.content.data

        try:
            if app.config.get('USE_SESSIONSTORE_NOT_DB'):
                if session.get(model_name) == None:
                    session[model_name] = {}

                if not model_identifier_int:
                    if not (session.get(model_name, {})
                            .get(model_identifier, None)):
                        session[model_name][model_identifier] = {
                            title_field_name: getattr(model, title_field_name)}

                session[model_name][(model_identifier_int or model_identifier)][field_name] = content.strftime('%H:%M:%S')
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


@blueprint.route("/time-update/<model_name>/<field_name>/<model_identifier>/", methods=["POST"])
@login_required
def time_update(model_name, field_name, model_identifier):
    return time_update_func(
        model_name=model_name,
        field_name=field_name,
        model_identifier=model_identifier)


@blueprint.route("/time-update-autosave/<model_name>/<field_name>/<model_identifier>/", methods=["POST"])
@login_required
def time_update_autosave(model_name, field_name, model_identifier):
    return time_update_func(
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

    try:
        model_identifier_int = int(model_identifier)
    except ValueError:
        model_identifier_int = None

    filter_by_kwargs = {
        identifier_field_name: model_identifier,
        'active': True}
    model = None

    if app.config.get('USE_SESSIONSTORE_NOT_DB'):
        model_store = session.get(model_name, None)
        model_dict = None

        if model_store and (type(model_store).__name__ == 'list'):
            try:
                model_dict = model_store[model_identifier_int]
            except KeyError:
                pass
        elif model_store and (type(model_store).__name__ == 'dict'):
            model_dict = model_store.get(model_identifier, None)

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

                if not model_identifier_int:
                    if not (session.get(model_name, {})
                            .get(model_identifier, None)):
                        session[model_name][model_identifier] = {
                            title_field_name: getattr(model, title_field_name)}

                session[model_name][(model_identifier_int or model_identifier)][field_name] = image
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


def add_func(model_name, is_autosave=False):
    try:
        v = app.config['EDITABLE_MODELS'][model_name]
    except KeyError:
        abort(404)

    if not(('is_createable' in v) and v['is_createable']):
        abort(404)

    try:
        model_classpath = v['classpath']
    except KeyError:
        raise ValueError('No class path defined in app config\'s EDITABLE_MODELS for model name "%s"' % model_name)

    try:
        title_field_name = v['title_field']
    except KeyError:
        raise ValueError('No title field defined in app config\'s EDITABLE_MODELS for model name "%s"' %  model_name)

    try:
        identifier_field_name = v['identifier_field']
    except KeyError:
        raise ValueError('No identifier field defined in app config\'s EDITABLE_MODELS for model name "%s"' %  model_name)

    try:
        weight_field_name = v['weight_field']
    except KeyError:
        weight_field_name = None

    model_class = get_model_class(model_classpath, model_name)

    form = Form()

    if form.validate_on_submit():
        model_name_friendly = model_name.replace('_', ' ').title()
        model = model_class.new_item()

        if ('image_fields' in v) and v['image_fields']:
            for k in v['image_fields']:
                setattr(model, k, placeholder_or_random_sample_image())

        if ('long_text_fields' in v) and v['long_text_fields']:
            for k in v['long_text_fields']:
                setattr(model, k, placeholder_or_random_sample_text())

        if (not app.config.get('USE_SESSIONSTORE_NOT_DB')) and weight_field_name:
            max_weight = model_class.max_weight()
            setattr(model, weight_field_name, (max_weight != None and (max_weight+1) or 0))

        try:
            if app.config.get('USE_SESSIONSTORE_NOT_DB'):
                if not session.get(model_name, None):
                    session[model_name] = []

                fields_to_save = []
                for k in ('text_fields', 'long_text_fields', 'image_fields'):
                    if (k in v) and v[k]:
                        fields_to_save.extend(v[k])

                values_to_save = {}
                for k in fields_to_save:
                    values_to_save[k] = getattr(model, k)

                if ('date_fields' in v) and v['date_fields']:
                    for k in v['date_fields']:
                        val = getattr(model, k, '')
                        if val:
                            val = val.strftime('%Y-%m-%d')

                        values_to_save[k] = val

                if ('time_fields' in v) and v['time_fields']:
                    for k in v['time_fields']:
                        val = getattr(model, k, '')
                        if val:
                            val = val.strftime('%H:%M:%S')

                        values_to_save[k] = val

                session[model_name].append(values_to_save)
            else:
                model.save()

            app.logger.info('{0} added: {1}; user: {2}'.format(model_name_friendly, model, current_user))

            if is_autosave:
                return Response('OK')
            else:
                flash('"{0}" has been added.'.format(getattr(model, title_field_name)), 'success')
        except IntegrityError as e:
            db.session.rollback()

            if is_autosave:
                return Response('ERROR')
            else:
                msg = (('violates unique constraint' in e.message)
                    and 'Error: a {0} with title "{1}" already exists.'.format(model_name_friendly, getattr(model, title_field_name))
                    or "Error adding {0}.".format(getattr(model, title_field_name)))
                flash(msg, 'danger')
    else:
        if is_autosave:
            return Response('ERROR')
        else:
            flash_errors(form)

    return redirect(url_for("public.home"))


@blueprint.route("/add/<model_name>/", methods=["POST"])
@login_required
def add(model_name):
    return add_func(model_name)


@blueprint.route("/add-autosave/<model_name>/", methods=["POST"])
@login_required
def add_autosave(model_name):
    return add_func(model_name, is_autosave=True)


def delete_func(model_name, model_identifier, is_bootbox=False):
    try:
        model_identifier_int = int(model_identifier)
    except ValueError:
        abort(404)

    try:
        v = app.config['EDITABLE_MODELS'][model_name]
    except KeyError:
        abort(404)

    if not(('is_deleteable' in v) and v['is_deleteable']):
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
        identifier_field_name: model_identifier_int,
        'active': True}
    model = None

    if app.config.get('USE_SESSIONSTORE_NOT_DB'):
        model_dict = ((session.get(model_name, [])
            and len(session[model_name]) >= (model_identifier_int+1))
            and session[model_name][model_identifier_int]
            or None)

        if model_dict:
            model = model_class(**model_dict)
    else:
        model = (model_class.query
            .filter_by(**filter_by_kwargs)
            .first())

    if not model:
        abort(404)

    form = Form()

    if form.validate_on_submit():
        title = getattr(model, title_field_name)
        model_name_friendly = model_name.replace('_', ' ').title()

        try:
            if app.config.get('USE_SESSIONSTORE_NOT_DB'):
                del session[model_name][model_identifier_int]
            else:
                model.delete()

            app.logger.info('{0} deleted: {1}; user: {2}'.format(model_name_friendly, title, current_user))

            if is_bootbox:
                return Response('OK')
            else:
                flash("{0} has been deleted.".format(title), 'success')
        except IntegrityError as e:
            db.session.rollback()

            if is_bootbox:
                return Response('ERROR')
            else:
                flash("Error deleting {0}.".format(title), 'danger')
    else:
        if is_bootbox:
            return Response('ERROR')
        else:
            flash_errors(form)

    return redirect(url_for("public.home"))


@blueprint.route("/delete/<model_name>/<model_identifier>/", methods=["POST"])
@login_required
def delete(model_name, model_identifier):
    return delete_func(model_name, model_identifier)


@blueprint.route("/delete-bootbox/<model_name>/<model_identifier>/", methods=["POST"])
@login_required
def delete_bootbox(model_name, model_identifier):
    return delete_func(model_name, model_identifier, is_bootbox=True)


def reorder_func(model_name, is_js=False):
    try:
        v = app.config['EDITABLE_MODELS'][model_name]
    except KeyError:
        abort(404)

    if not(('is_reorderable' in v) and v['is_reorderable']):
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
        weight_field_name = v['weight_field']
    except KeyError:
        raise ValueError('No weight field defined in app config\'s EDITABLE_MODELS for model name "%s"' %  model_name)

    model_class = get_model_class(model_classpath, model_name)

    weight_field = getattr(model_class, weight_field_name)
    reorder_form_prefix = v.get('reorder_form_prefix', '')

    if app.config.get('USE_SESSIONSTORE_NOT_DB'):
        items = [i for i, v in enumerate(session[model_name]) if v]
    else:
        items = [getattr(o, identifier_field_name) for o in (model_class.query
            .filter_by(active=True)
            .order_by(weight_field).all())]

    form = ReorderForm(items=items, prefix=reorder_form_prefix)
    item_weights = None

    if form.validate_on_submit():
        model_name_friendly = model_name.replace('_', ' ').title()

        if app.config.get('USE_SESSIONSTORE_NOT_DB'):
            item_weights = [{'value': v, 'weight': (i-1)} for i, v in enumerate(session[model_name])]

            for item_form in form.items:
                item_weights[int(item_form.identifier.data)]['weight'] = int(item_form.weight.data)

            item_weights = sorted(item_weights, key=itemgetter('weight'))
        else:
            for item_form in form.items:
                filter_by_kwargs = {
                    identifier_field_name: item_form.identifier.data,
                    'active': True}

                item = (model_class.query
                    .filter_by(**filter_by_kwargs)
                    .first())
                item.weight = item_form.weight.data
                db.session.add(item)

        try:
            if app.config.get('USE_SESSIONSTORE_NOT_DB'):
                session[model_name] = [v['value'] for v in item_weights]
            else:
                db.session.commit()

            app.logger.info('{0}s re-ordered: user: {1}'.format(model_name_friendly, current_user))

            if is_js:
                return Response('OK')
            else:
                flash("{0}s have been re-ordered.".format(model_name_friendly), 'success')
        except IntegrityError as e:
            db.session.rollback()

            if is_js:
                return Response('ERROR')
            else:
                flash("Error re-ordering {0}.".format(model_name_friendly), 'danger')
    else:
        if is_js:
            return Response('ERROR')
        else:
            flash_errors(form)

    return redirect(url_for("public.home"))


@blueprint.route("/reorder/<model_name>/", methods=["POST"])
@login_required
def reorder(model_name):
    return reorder_func(model_name)


@blueprint.route("/reorder-js/<model_name>/", methods=["POST"])
@login_required
def reorder_js(model_name):
    return reorder_func(model_name, is_js=True)
