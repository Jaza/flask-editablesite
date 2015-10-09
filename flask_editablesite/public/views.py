# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import current_app as app
from flask import (Blueprint, request, render_template, flash, url_for,
                    redirect, session, send_from_directory)
from flask_login import (login_user, login_required, logout_user,
                         current_user)

from flask_editablesite.extensions import login_manager
from flask_editablesite.user.models import User
from flask_editablesite.contentblock.models import ShortTextContentBlock, RichTextContentBlock, ImageContentBlock
from flask_editablesite.editable.forms import TextEditForm, LongTextEditForm, ImageEditForm
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
                'image': o.image,
                'model': o}
        for o in ImageContentBlock.default_content().values()}

    if app.config.get('USE_SESSIONSTORE_NOT_DB'):
        for slug, o in session.get('image_content_block', {}).items():
            ic_blocks[slug] = {
                'title': o['title'],
                'image': o['image']}
    else:
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

    template_vars = dict(
        login_form=login_form,
        stc_blocks=stc_blocks,
        rtc_blocks=rtc_blocks,
        ic_blocks=ic_blocks)

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
