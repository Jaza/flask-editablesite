# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
import os

from flask import current_app as app
from flask import (Blueprint, request, render_template, flash, url_for,
                    redirect, session, send_from_directory)
from flask_wtf import Form
from flask_login import (login_user, login_required, logout_user,
                         current_user)

from flask_editablesite.extensions import login_manager
from flask_editablesite.user.models import User
from flask_editablesite.contentblock.models import ShortTextContentBlock, RichTextContentBlock, ImageContentBlock
from flask_editablesite.gallery.models import GalleryItem
from flask_editablesite.editable.forms import TextEditForm, LongTextEditForm, ImageEditForm, ReorderForm
from flask_editablesite.editable.sample_images import placeholder_or_random_sample_image
from flask_editablesite.editable.sample_text import placeholder_or_random_sample_text
from flask_editablesite.public.forms import LoginForm
from flask_editablesite.utils import flash_errors
from flask_editablesite.database import db

blueprint = Blueprint('public', __name__, static_folder="../static")


@login_manager.user_loader
def load_user(id):
    int_id = None
    if not app.config.get('USE_SESSIONSTORE_NOT_DB'):
        try:
            int_id = int(id)
        except ValueError:
            return None

    return (app.config.get('USE_SESSIONSTORE_NOT_DB')
        # Load the dummy user if set to 'sessionstore' instead of 'db'
        and User.sessionstore_user()
        # Otherwise load the actual logged-in user from the DB.
        or User.get_by_id(int_id))


@blueprint.route("/")
def home():
    if current_user.is_authenticated() and (not current_user.active):
        logout_user()

    login_form = (not current_user.is_authenticated()) and LoginForm() or None

    # Short text blocks
    stc_blocks = {
            o.slug: {
                'title': o.title,
                'content': o.content,
                'model': o}
        for o in ShortTextContentBlock.default_content().values()}

    if app.config.get('USE_SESSIONSTORE_NOT_DB'):
        for slug, o in session.get('short_text_content_block', {}).items():
            stc_blocks[slug] = {
                'title': o['title'],
                'content': o['content']}
    else:
        for o in (ShortTextContentBlock.query
                .filter_by(active=True)
                .all()):
            stc_blocks[o.slug] = {
                'title': o.title,
                'content': o.content}

    if current_user.is_authenticated():
        for k in stc_blocks.keys():
            form = TextEditForm(
                content=stc_blocks[k]['content'])

            form.content.label = stc_blocks[k]['title']

            stc_blocks[k]['form'] = form

    # Rich text blocks
    rtc_blocks = {
            o.slug: {
                'title': o.title,
                'content': o.content,
                'model': o}
        for o in RichTextContentBlock.default_content().values()}

    if app.config.get('USE_SESSIONSTORE_NOT_DB'):
        for slug, o in session.get('rich_text_content_block', {}).items():
            rtc_blocks[slug] = {
                'title': o['title'],
                'content': o['content']}
    else:
        for o in (RichTextContentBlock.query
                .filter_by(active=True)
                .all()):
            rtc_blocks[o.slug] = {
                'title': o.title,
                'content': o.content}

    if current_user.is_authenticated():
        for k in rtc_blocks.keys():
            form = LongTextEditForm(
                content=rtc_blocks[k]['content'])

            form.content.label = rtc_blocks[k]['title']

            rtc_blocks[k]['form'] = form

    # Image blocks
    ic_blocks = {
            o.slug: {
                'title': o.title,
                'image': o.image_or_placeholder,
                'model': o}
        for o in ImageContentBlock.default_content().values()}

    if app.config.get('USE_SESSIONSTORE_NOT_DB'):
        for slug, o in ic_blocks.items():
            if session.get('image_content_block') == None:
                session['image_content_block'] = {}

            if session.get('image_content_block', {}).get(slug, None):
                filepath = os.path.join(
                    app.config['MEDIA_FOLDER'],
                    session['image_content_block'][slug]['image'])

                # If the placeholder image defined in session storage
                # doesn't exist on the filesystem (e.g. if Heroku has
                # wiped the filesystem due to app restart), clear this
                # model's session storage.
                if not os.path.exists(filepath):
                    del session['image_content_block'][slug]

            if not (session.get('image_content_block', {})
                    .get(slug, None)):
                # If this model isn't currently saved to session storage,
                # set its image now (could be a random sample) and save.
                session['image_content_block'][slug] = {
                    'title': o['title'],
                    'image': placeholder_or_random_sample_image()}

        for slug, o in session.get('image_content_block', {}).items():
            ic_blocks[slug] = {
                'title': o['title'],
                'image': o['image']}
    else:
        for slug, o in ic_blocks.items():
            if not(ImageContentBlock.query
                    .filter_by(slug=slug)
                    .first()):
                # If this model isn't currently saved to the DB,
                # set its image now (could be a random sample) and save.
                model = o['model']
                model.image = placeholder_or_random_sample_image()

                try:
                    model.save()
                except IntegrityError as e:
                    db.session.rollback()
                    raise e

        for o in (ImageContentBlock.query
                .filter_by(active=True)
                .all()):
            ic_blocks[o.slug] = {
                'title': o.title,
                'image': o.image}

    if current_user.is_authenticated():
        for k in ic_blocks.keys():
            form = ImageEditForm(
                image=ic_blocks[k]['image'])

            form.image.label = ic_blocks[k]['title']

            ic_blocks[k]['form'] = form

    # Gallery items
    gallery_limit = app.config['GALLERY_LIMIT']

    if app.config.get('USE_SESSIONSTORE_NOT_DB'):
        gallery_count = len(session.get('gallery_item', []))
    else:
        gallery_count = (GalleryItem.query
            .filter_by(active=True)
            .count())

    if not gallery_count:
        default_gallery_items = GalleryItem.default_content()

        if app.config.get('USE_SESSIONSTORE_NOT_DB'):
            session['gallery_item'] = ['']

            for o in default_gallery_items:
                # If this model isn't currently saved to session storage,
                # set its image and text content now (could be random
                # samples) and save.
                session['gallery_item'].append({
                    'title': o.title,
                    'image': placeholder_or_random_sample_image(),
                    'content': placeholder_or_random_sample_text(),
                    'date_taken': o.date_taken})
        else:
            curr_weight = 0

            for o in default_gallery_items:
                # If this model isn't currently saved to the DB,
                # set its image and text content now (could be random
                # samples) and save.
                o.image = placeholder_or_random_sample_image()
                o.content = placeholder_or_random_sample_text()
                o.weight = curr_weight

                try:
                    o.save()
                    curr_weight += 1
                except IntegrityError as e:
                    db.session.rollback()
                    raise e

        gallery_count = len(default_gallery_items)

    is_gallery_showmore = request.args.get('gallery_showmore', None) == '1'

    is_gallery_showlimited = (
        (not current_user.is_authenticated()) and
        (not is_gallery_showmore) and
        (gallery_count > gallery_limit))

    if app.config.get('USE_SESSIONSTORE_NOT_DB'):
        if session.get('gallery_item') == None:
            session['gallery_item'] = ['']

        for id, o in enumerate(session.get('gallery_item', [])):
            if o:
                filepath = os.path.join(
                    app.config['MEDIA_FOLDER'],
                    session['gallery_item'][id]['image'])

                # If the placeholder image defined in session storage
                # doesn't exist on the filesystem (e.g. if Heroku has
                # wiped the filesystem due to app restart), set a new image
                # for this model.
                if not os.path.exists(filepath):
                    session['gallery_item'][id]['image'] = placeholder_or_random_sample_image()

        gallery_items = []
        for id, o in enumerate(session['gallery_item']):
            if o:
                model = GalleryItem(**o)
                model.id = id
                model.weight = id-1
                gallery_items.append(model)
    else:
        gallery_items = (GalleryItem.query
            .filter_by(active=True)
            .order_by(GalleryItem.weight))

    if is_gallery_showlimited:
        if app.config.get('USE_SESSIONSTORE_NOT_DB'):
            gallery_items = gallery_items[:gallery_limit]
        else:
            gallery_items = (gallery_items
                .limit(gallery_limit))

    if not app.config.get('USE_SESSIONSTORE_NOT_DB'):
        gallery_items = gallery_items.all()

    gallery_forms = {}
    if current_user.is_authenticated():
        for gi in gallery_items:
            gallery_forms[gi.id] = {
                'title': TextEditForm(content=gi.title),
                'image': ImageEditForm(image=gi.image),
                'content': LongTextEditForm(content=gi.content),
                'date_taken': TextEditForm(content=gi.date_taken)}

            if current_user.is_authenticated():
                gallery_forms[gi.id]['delete'] = Form()

    gi_add_form = current_user.is_authenticated() and Form() or None

    gi_reorder_form = None

    if current_user.is_authenticated():
        if app.config.get('USE_SESSIONSTORE_NOT_DB'):
            items = [{'identifier': i, 'weight': i-1} for i, v in enumerate(session['gallery_item']) if v]
        else:
            items = [{'identifier': gi.id, 'weight': gi.weight} for gi in (GalleryItem.query
                .filter_by(active=True)
                .order_by(GalleryItem.weight).all())]

        gi_reorder_form = ReorderForm(items=items, prefix='gallery_')

    template_vars = dict(
        login_form=login_form,
        stc_blocks=stc_blocks,
        rtc_blocks=rtc_blocks,
        ic_blocks=ic_blocks,
        gallery_items=gallery_items,
        is_gallery_showlimited=is_gallery_showlimited,
        gallery_forms=gallery_forms,
        gi_add_form=gi_add_form,
        gi_reorder_form=gi_reorder_form)

    return render_template("public/home.html",
                           **template_vars)


@blueprint.route("/login/", methods=["POST"])
def login():
    form = LoginForm(request.form)

    # Handle logging in
    if form.validate_on_submit():
        login_user(form.user, remember=True)
        app.logger.info('User logged in: {0}'.format(form.user))
        flash("You are logged in.", 'success')
    else:
        flash_errors(form)

    return redirect(url_for("public.home"))


@blueprint.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('You are logged out.', 'info')
    return redirect(url_for('public.home'))


@blueprint.route('/robots.txt')
@blueprint.route('/sitemap.xml')
def static_from_root():
    # Thanks to:
    # http://stackoverflow.com/a/14054039/2066849
    return send_from_directory(app.static_folder, request.path[1:])
