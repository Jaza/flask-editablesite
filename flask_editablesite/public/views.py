# -*- coding: utf-8 -*-
"""Public section, including homepage."""

from datetime import datetime, date
import os

from flask import current_app as app
from flask import (Blueprint, request, render_template, flash, url_for,
                   redirect, session, send_from_directory)
from flask_wtf import Form
from flask_mail import Message
from flask_login import (login_user, login_required, logout_user,
                         current_user)
from sqlalchemy.exc import IntegrityError

from flask_editablesite.extensions import db, login_manager, mail
from flask_editablesite.user.models import User
from flask_editablesite.contentblock.models import (
    ShortTextContentBlock, RichTextContentBlock, ImageContentBlock)
from flask_editablesite.gallery.models import GalleryItem
from flask_editablesite.event.models import Event
from flask_editablesite.editable.forms import (
    TextEditForm, TextOptionalEditForm, LongTextEditForm,
    ImageEditForm, ReorderForm, DateEditForm,
    DateOptionalEditForm, TimeOptionalEditForm)
from flask_editablesite.editable.sample_images import (
    placeholder_or_random_sample_image,)
from flask_editablesite.editable.sample_text import (
    placeholder_or_random_sample_text,)
from flask_editablesite.public.forms import (
    LoginForm, ContactForm)
from flask_editablesite.utils import flash_errors

blueprint = Blueprint('public', __name__, static_folder="../static")


@login_manager.user_loader
def load_user(id):
    int_id = None
    if not app.config.get('USE_SESSIONSTORE_NOT_DB'):
        try:
            int_id = int(id)
        except ValueError:
            return None

    return (
        app.config.get('USE_SESSIONSTORE_NOT_DB')
        # Load the dummy user if set to 'sessionstore' instead of 'db'
        and User.sessionstore_user()
        # Otherwise load the actual logged-in user from the DB.
        or User.get_by_id(int_id))


def get_stc_blocks():
    """Gets short text blocks."""

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
        for o in (
            ShortTextContentBlock.query
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

    return stc_blocks


def get_rtc_blocks():
    """Gets rich text blocks."""

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
        for o in (
            RichTextContentBlock.query
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

    return rtc_blocks


def get_sessionstore_ic_blocks(ic_blocks):
    """Gets image blocks from the session store."""

    for slug, o in ic_blocks.items():
        if session.get('image_content_block') is None:
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

    return ic_blocks


def get_db_ic_blocks(ic_blocks):
    """Gets image blocks from the database."""

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

    for o in (
        ImageContentBlock.query
            .filter_by(active=True)
            .all()):
        ic_blocks[o.slug] = {
            'title': o.title,
            'image': o.image}

    return ic_blocks


def get_ic_blocks():
    """Gets image blocks."""

    ic_blocks = {
        o.slug: {
            'title': o.title,
            'image': o.image_or_placeholder,
            'model': o}
        for o in ImageContentBlock.default_content().values()}

    if app.config.get('USE_SESSIONSTORE_NOT_DB'):
        ic_blocks = get_sessionstore_ic_blocks(ic_blocks)
    else:
        ic_blocks = get_db_ic_blocks(ic_blocks)

    if current_user.is_authenticated():
        for k in ic_blocks.keys():
            form = ImageEditForm(
                image=ic_blocks[k]['image'])

            form.image.label = ic_blocks[k]['title']

            ic_blocks[k]['form'] = form

    return ic_blocks


def get_default_gallery_items():
    """Gets the default gallery items."""

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

    return default_gallery_items


def get_gallery_items():
    """Gets all gallery items."""

    if app.config.get('USE_SESSIONSTORE_NOT_DB'):
        if session.get('gallery_item') is None:
            session['gallery_item'] = ['']

        for id, o in enumerate(session.get('gallery_item', [])):
            if o:
                filepath = os.path.join(
                    app.config['MEDIA_FOLDER'],
                    session['gallery_item'][id]['image'])

                # If the placeholder image defined in session storage
                # doesn't exist on the filesystem (e.g. if Heroku has
                # wiped the filesystem due to app restart), set a new
                # image for this model.
                if not os.path.exists(filepath):
                    session['gallery_item'][id]['image'] = (
                        placeholder_or_random_sample_image())

        gallery_items = []
        for id, o in enumerate(session['gallery_item']):
            if o:
                model = GalleryItem(**o)
                model.id = id
                model.weight = id-1
                gallery_items.append(model)
    else:
        gallery_items = (
            GalleryItem.query
                       .filter_by(active=True)
                       .order_by(GalleryItem.weight))

    return gallery_items


def get_default_events():
    """Gets default events."""

    default_events = Event.default_content()

    if app.config.get('USE_SESSIONSTORE_NOT_DB'):
        session['event'] = ['']

        for o in default_events:
            # If this model isn't currently saved to session
            # storage, save it now.
            session['event'].append({
                'title': o.title,
                'start_date': o.start_date.strftime('%Y-%m-%d'),
                'end_date': (
                    o.end_date
                    and o.end_date.strftime('%Y-%m-%d')
                    or ''),
                'start_time': (
                    o.start_time
                    and o.start_time.strftime('%H:%M:%S')
                    or ''),
                'end_time': (
                    o.end_time
                    and o.end_time.strftime('%H:%M:%S')
                    or ''),
                'event_url': o.event_url,
                'location_name': o.location_name,
                'location_url': o.location_url})
    else:
        for o in default_events:
            # If this model isn't currently saved to the DB,
            # save it now.
            try:
                o.save()
            except IntegrityError as e:
                db.session.rollback()
                raise e

    return default_events


def get_events():
    """Gets upcoming and past events."""

    events_upcoming = []
    events_past = []

    if app.config.get('USE_SESSIONSTORE_NOT_DB'):
        if session.get('event') is None:
            session['event'] = ['']

        for id, o in enumerate(session['event']):
            if o:
                dt_now_str = datetime.now().strftime('%Y-%m-%d')
                o_d = {
                    'title': o['title'],
                    'start_date': (
                        datetime.strptime(o['start_date'], '%Y-%m-%d')
                        .date()),
                    'end_date': (
                        o['end_date']
                        and (
                            datetime.strptime(
                                o['end_date'], '%Y-%m-%d')
                            .date())
                        or None),
                    'start_time': (
                        o['start_time']
                        and (
                            datetime.strptime(
                                dt_now_str + ' ' + o['start_time'],
                                '%Y-%m-%d %H:%M:%S')
                            .time())
                        or None),
                    'end_time': (
                        o['end_time']
                        and (
                            datetime.strptime(
                                dt_now_str + ' ' + o['end_time'],
                                '%Y-%m-%d %H:%M:%S')
                            .time()) or None),
                    'event_url': o['event_url'],
                    'location_name': o['location_name'],
                    'location_url': o['location_url']}
                model = Event(**o_d)
                model.id = id

                if model.start_date >= date.today():
                    events_upcoming.append(model)
                else:
                    events_past.append(model)

        events_upcoming = sorted(
            events_upcoming, key=lambda o: o.start_date)
        events_past = sorted(
            events_past, key=lambda o: o.start_date, reverse=True)
    else:
        events_upcoming = (
            Event.query
                 .filter_by(active=True)
                 .filter(Event.start_date >= date.today())
                 .order_by(Event.start_date, Event.start_time))

        events_past = (
            Event.query
                 .filter_by(active=True)
                 .filter(Event.start_date < date.today())
                 .order_by(Event.start_date.desc(),
                           Event.start_time.desc()))

    return (events_upcoming, events_past)


def get_gi_vars():
    """Gets gallery item variables."""

    gallery_limit = app.config['GALLERY_LIMIT']

    if app.config.get('USE_SESSIONSTORE_NOT_DB'):
        gallery_count = len(session.get('gallery_item', []))
    else:
        gallery_count = (
            GalleryItem.query
                       .filter_by(active=True)
                       .count())

    if not gallery_count:
        default_gallery_items = get_default_gallery_items()
        gallery_count = len(default_gallery_items)

    is_gallery_showmore = request.args.get('gallery_showmore', None) == '1'

    is_gallery_showlimited = (
        (not current_user.is_authenticated()) and
        (not is_gallery_showmore) and
        (gallery_count > gallery_limit))

    gallery_items = get_gallery_items()

    if is_gallery_showlimited:
        if app.config.get('USE_SESSIONSTORE_NOT_DB'):
            gallery_items = gallery_items[:gallery_limit]
        else:
            gallery_items = gallery_items.limit(gallery_limit)

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

    return (
        gallery_items,
        is_gallery_showlimited,
        gallery_forms)


def get_gi_reorder_form():
    """Gets the gallery item re-ordering form."""

    gi_reorder_form = None

    if current_user.is_authenticated():
        if app.config.get('USE_SESSIONSTORE_NOT_DB'):
            items = [
                {'identifier': i, 'weight': i-1}
                for i, v in enumerate(session['gallery_item']) if v]
        else:
            items = [
                {'identifier': gi.id, 'weight': gi.weight}
                for gi in (
                    GalleryItem.query
                               .filter_by(active=True)
                               .order_by(GalleryItem.weight).all())]

        gi_reorder_form = ReorderForm(items=items, prefix='gallery_')

    return gi_reorder_form


def get_event_vars():
    """Gets event variables."""

    event_upcoming_limit = app.config['EVENT_UPCOMING_LIMIT']

    if app.config.get('USE_SESSIONSTORE_NOT_DB'):
        event_upcoming_count = len([
            o for o in session.get('event', [])
            if (o and (
                datetime.strptime(o['start_date'], '%Y-%m-%d').date()
                >= date.today()))])
    else:
        event_upcoming_count = (
            Event.query
                 .filter_by(active=True)
                 .filter(Event.start_date >= date.today())
                 .count())

    event_past_limit = app.config['EVENT_PAST_LIMIT']

    if app.config.get('USE_SESSIONSTORE_NOT_DB'):
        event_past_count = len([
            o for o in session.get('event', [])
            if (o and (
                datetime.strptime(o['start_date'], '%Y-%m-%d').date()
                < date.today()))])
    else:
        event_past_count = (
            Event.query
                 .filter_by(active=True)
                 .filter(Event.start_date < date.today())
                 .count())

    if (not event_upcoming_count) and (not event_past_count):
        default_events = get_default_events()

        event_upcoming_count = len([
            o for o in default_events
            if o.start_date >= date.today()])

        event_past_count = len([
            o for o in default_events
            if o.start_date < date.today()])

    is_events_showmore = (
        request.args.get('events_showmore', None) == '1')

    is_events_showlimited = (
        (not current_user.is_authenticated()) and
        (not is_events_showmore) and
        (
            (event_upcoming_count > event_upcoming_limit) or
            (event_past_count > event_past_limit)))

    events_upcoming, events_past = get_events()

    if is_events_showlimited:
        if app.config.get('USE_SESSIONSTORE_NOT_DB'):
            events_upcoming = events_upcoming[:event_upcoming_limit]
            events_past = events_past[:event_past_limit]
        else:
            events_upcoming = (
                events_upcoming.limit(event_upcoming_limit))

            events_past = (
                events_past.limit(event_past_limit))

    if not app.config.get('USE_SESSIONSTORE_NOT_DB'):
        events_upcoming = events_upcoming.all()
        events_past = events_past.all()

    event_forms = {}
    if current_user.is_authenticated():
        for event in (events_upcoming + events_past):
            event_forms[event.id] = {
                'title': TextEditForm(content=event.title),
                'event_url': TextOptionalEditForm(
                    content=event.event_url),
                'start_date': DateEditForm(
                    content=event.start_date),
                'end_date': DateOptionalEditForm(
                    content=event.end_date),
                'start_time': TimeOptionalEditForm(
                    content=event.start_time),
                'end_time': TimeOptionalEditForm(
                    content=event.end_time),
                'location_name': TextOptionalEditForm(
                    content=event.location_name),
                'location_url': TextOptionalEditForm(
                    content=event.location_url)}

            if current_user.is_authenticated():
                event_forms[event.id]['delete'] = Form()

    return (
        events_upcoming,
        events_past,
        is_events_showlimited,
        event_forms)


@blueprint.route("/")
def home():
    if current_user.is_authenticated() and (not current_user.active):
        logout_user()

    login_form = (not current_user.is_authenticated()) and LoginForm() or None

    # Gallery items
    (
        gallery_items,
        is_gallery_showlimited,
        gallery_forms) = get_gi_vars()

    gi_add_form = current_user.is_authenticated() and Form() or None
    gi_reorder_form = get_gi_reorder_form()

    # Events
    (
        events_upcoming,
        events_past,
        is_events_showlimited,
        event_forms) = get_event_vars()

    event_add_form = current_user.is_authenticated() and Form() or None

    template_vars = dict(
        login_form=login_form,
        contact_form=ContactForm(),
        stc_blocks=get_stc_blocks(),
        rtc_blocks=get_rtc_blocks(),
        ic_blocks=get_ic_blocks(),
        gallery_items=gallery_items,
        is_gallery_showlimited=is_gallery_showlimited,
        gallery_forms=gallery_forms,
        gi_add_form=gi_add_form,
        gi_reorder_form=gi_reorder_form,
        events_upcoming=events_upcoming,
        events_past=events_past,
        is_events_showlimited=is_events_showlimited,
        event_forms=event_forms,
        event_add_form=event_add_form)

    return render_template("public/home.html",
                           **template_vars)


@blueprint.route("/contact/", methods=["POST"])
def contact():
    form = ContactForm(request.form)

    if form.validate_on_submit():
        subject = "New message from {0} contact form".format(
            app.config['SITE_NAME'])

        body = "\nFrom: {0} <{1}>\n".format(
            form.name.data,
            form.email.data)

        if form.phone.data:
            body += "Phone: {0}\n".format(form.phone.data)

        body += "\n\n{0}\n\n-----\n\n".format(form.message.data)
        body += "This is an auto-generated email from {0}.\n".format(
            app.config['SITE_NAME'])

        log_msg = "Contact form submission\n"
        log_msg += "Sent by: <{0}>\n".format(
            app.config['MAIL_DEFAULT_SENDER'])
        log_msg += "Sent to: {0}\n".format(
            app.config['CONTACT_EMAIL_RECIPIENTS'])
        log_msg += "Subject: {0}\n".format(subject)
        log_msg += body

        app.logger.info(log_msg)

        if (not app.debug) and app.config['CONTACT_EMAIL_RECIPIENTS']:
            msg = Message(
                subject,
                recipients=app.config['CONTACT_EMAIL_RECIPIENTS'])

            msg.body = body

            mail.send(msg)

        flash("Your message has been sent.", 'success')
    else:
        flash_errors(form)

    return redirect(url_for("public.home"))


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
