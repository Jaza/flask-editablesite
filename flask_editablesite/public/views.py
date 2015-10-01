# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import current_app as app
from flask import (Blueprint, request, render_template, flash, url_for,
                    redirect, session, send_from_directory)
from flask_login import (login_user, login_required, logout_user,
                         current_user)

from flask_editablesite.extensions import login_manager
from flask_editablesite.user.models import User
from flask_editablesite.contentblock.models import ShortTextContentBlock
from flask_editablesite.editable.forms import TextEditForm
from flask_editablesite.public.forms import LoginForm
from flask_editablesite.utils import flash_errors
from flask_editablesite.database import db

blueprint = Blueprint('public', __name__, static_folder="../static")


@login_manager.user_loader
def load_user(id):
    return (app.config.get('USE_SESSIONSTORE_NOT_DB')
        # Load the dummy user if set to 'sessionstore' instead of 'db'
        and User.sessionstore_user()
        # Otherwise load the actual logged-in user from the DB.
        or User.get_by_id(int(id)))


@blueprint.route("/")
def home():
    if current_user.is_authenticated() and (not current_user.active):
        logout_user()

    login_form = (not current_user.is_authenticated()) and LoginForm() or None

    stc_blocks = {
            o.slug: {
                'title': o.title,
                'content': o.content,
                'model': o}
        for o in ShortTextContentBlock.default_content().values()}

    for o in (ShortTextContentBlock.query
            .filter_by(active=True)
            .all()):
        stc_blocks[o.slug] = {
            'title': o.title,
            'content': o.content,
            'model': o}

    if current_user.is_authenticated():
        for k in stc_blocks.keys():
            form = TextEditForm(
                obj=stc_blocks[k]['model'])

            form.content.label = stc_blocks[k]['title']

            stc_blocks[k]['form'] = form

    template_vars = dict(
        login_form=login_form,
        stc_blocks=stc_blocks)

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
