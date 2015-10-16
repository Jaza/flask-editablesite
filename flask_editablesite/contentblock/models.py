# -*- coding: utf-8 -*-
from sqlalchemy import event
from slugify import slugify

from flask import current_app as app

from flask_editablesite.database import (
    Column,
    db,
    Model,
    SurrogatePK,
    Slugged,
    TimeStamped,
    Confirmable,
    update_slug_before_save,
    update_timestamps_before_insert,
    update_timestamps_before_update,
    update_confirmedat_before_save,
)


class ShortTextContentBlock(SurrogatePK, Slugged, TimeStamped, Confirmable, Model):
    __tablename__ = 'short_text_content_block'

    content = Column(db.String(255), nullable=False, default='')

    __table_args__ = (
        db.UniqueConstraint('slug', name='_stcb_slug_uc'),
        db.Index('_stcb_slug_active_ix', 'slug', 'active'))

    def __repr__(self):
        return self.title

    @classmethod
    def default_content(cls):
        ret = {}

        title = 'Site welcome prefix'
        slug = slugify(title, to_lower=True)
        ret[slug] = cls(title=title, slug=slug, content='Welcome to', active=True)

        title = 'Site byline'
        slug = slugify(title, to_lower=True)
        ret[slug] = cls(title=title, slug=slug, content='A template for building a small marketing web site in Flask where all content is live editable.', active=True)

        title = 'Site byline link title'
        slug = slugify(title, to_lower=True)
        ret[slug] = cls(title=title, slug=slug, content='Learn more', active=True)

        title = 'Site byline link URL'
        slug = slugify(title, to_lower=True)
        ret[slug] = cls(title=title, slug=slug, content='https://github.com/Jaza/flask-editablesite', active=True)

        title = 'About title'
        slug = slugify(title, to_lower=True)
        ret[slug] = cls(title=title, slug=slug, content='About', active=True)

        title = 'Gallery title'
        slug = slugify(title, to_lower=True)
        ret[slug] = cls(title=title, slug=slug, content='Gallery', active=True)

        title = 'Events title'
        slug = slugify(title, to_lower=True)
        ret[slug] = cls(title=title, slug=slug, content='Events', active=True)

        return ret


event.listen(ShortTextContentBlock, 'before_insert', update_timestamps_before_insert)
event.listen(ShortTextContentBlock, 'before_update', update_timestamps_before_update)

event.listen(ShortTextContentBlock, 'before_insert', update_confirmedat_before_save)
event.listen(ShortTextContentBlock, 'before_update', update_confirmedat_before_save)

event.listen(ShortTextContentBlock, 'before_insert', update_slug_before_save)
event.listen(ShortTextContentBlock, 'before_update', update_slug_before_save)


class RichTextContentBlock(SurrogatePK, Slugged, TimeStamped, Confirmable, Model):
    __tablename__ = 'rich_text_content_block'

    content = Column(db.Text(), nullable=False, default='')

    __table_args__ = (
        db.UniqueConstraint('slug', name='_rtcb_slug_uc'),
        db.Index('_rtcb_slug_active_ix', 'slug', 'active'))

    def __repr__(self):
        return self.title

    @classmethod
    def default_content(cls):
        ret = {}

        title = 'About text (left column)'
        slug = slugify(title, to_lower=True)
        ret[slug] = cls(title=title, slug=slug, content='<p>The aim of this app is to demonstrate that, with the help of modern JS libraries, and with some well-thought-out server-side snippets, it\'s now perfectly possible to "bake in" live in-place editing for virtually every content element in a typical brochureware site.</p>', active=True)

        title = 'About text (right column)'
        slug = slugify(title, to_lower=True)
        ret[slug] = cls(title=title, slug=slug, content='<p>This app is not a CMS. On the contrary, think of it as a proof-of-concept alternative to a CMS. An alternative where there\'s no "admin area", there\'s no "editing mode", and there\'s no "preview button".</p>', active=True)

        title = 'About text (below columns)'
        slug = slugify(title, to_lower=True)
        ret[slug] = cls(title=title, slug=slug, content="<p>There's only direct manipulation.</p>", active=True)

        return ret


event.listen(RichTextContentBlock, 'before_insert', update_timestamps_before_insert)
event.listen(RichTextContentBlock, 'before_update', update_timestamps_before_update)

event.listen(RichTextContentBlock, 'before_insert', update_confirmedat_before_save)
event.listen(RichTextContentBlock, 'before_update', update_confirmedat_before_save)

event.listen(RichTextContentBlock, 'before_insert', update_slug_before_save)
event.listen(RichTextContentBlock, 'before_update', update_slug_before_save)


class ImageContentBlock(SurrogatePK, Slugged, TimeStamped, Confirmable, Model):
    __tablename__ = 'image_content_block'

    image = Column(db.String(255), nullable=False, default='')

    __table_args__ = (
        db.UniqueConstraint('slug', name='_icb_slug_uc'),
        db.Index('_icb_slug_active_ix', 'slug', 'active'))

    def __repr__(self):
        return self.title

    @property
    def image_path(self):
        return self.image and '%s%s' % (app.config['UPLOADS_RELATIVE_PATH'], self.image) or None

    @property
    def image_url(self):
        if not self.image:
            return None

        return url_for('static', filename=self.image_path, _external=True)

    @property
    def image_or_placeholder(self):
        return self.image or app.config['EDITABLE_PLACEHOLDER_IMAGE_RELATIVE_PATH']

    @classmethod
    def default_content(cls):
        ret = {}

        title = 'Site logo'
        slug = slugify(title, to_lower=True)
        ret[slug] = cls(title=title, slug=slug, image=app.config['EDITABLE_PLACEHOLDER_IMAGE_RELATIVE_PATH'], active=True)

        return ret


event.listen(ImageContentBlock, 'before_insert', update_timestamps_before_insert)
event.listen(ImageContentBlock, 'before_update', update_timestamps_before_update)

event.listen(ImageContentBlock, 'before_insert', update_confirmedat_before_save)
event.listen(ImageContentBlock, 'before_update', update_confirmedat_before_save)

event.listen(ImageContentBlock, 'before_insert', update_slug_before_save)
event.listen(ImageContentBlock, 'before_update', update_slug_before_save)
