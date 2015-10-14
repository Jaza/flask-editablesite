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
        ret[slug] = cls(title=title, slug=slug, content='<p>Grkjg rhekjgreh gkje hgkrejgh erkjgerh gjkerhg kejrg herkjgehr kgjerhg kjreg herkjgehr kgjerh gkjerhg kejrgh erkjgehr kjgerh gkjerhg erkjg herkjg ehr jgkerh jgkreg.</p>', active=True)

        title = 'About text (right column)'
        slug = slugify(title, to_lower=True)
        ret[slug] = cls(title=title, slug=slug, content='<p>Jkjg rekgre gkjg hkjrgher kjgrhe gkjerhg ekrjgh erkjgeh gkjergh erkjghe rkjgerh gkejrg herkjghre kjgerh gkjerhg erkjg herkgj.</p>', active=True)

        title = 'About text (below columns)'
        slug = slugify(title, to_lower=True)
        ret[slug] = cls(title=title, slug=slug, content='<p>Vkgjre kgjreh gkjregh erkjgehr kgjeh gerkjg.</p>', active=True)

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
