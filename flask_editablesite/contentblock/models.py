# -*- coding: utf-8 -*-
from sqlalchemy import event
from slugify import slugify

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

        title = 'Site byline'
        slug = slugify(title, to_lower=True)
        ret[slug] = cls(title=title, slug=slug, content='A template for building a small marketing web site in Flask where all content is live editable.', active=True)

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
        from flask import current_app as app
        return self.image and '%s%s' % (app.config['UPLOADS_RELATIVE_PATH'], self.image) or None

    @property
    def image_url(self):
        if not self.image:
            return None

        return url_for('static', filename=self.image_path, _external=True)


event.listen(ImageContentBlock, 'before_insert', update_timestamps_before_insert)
event.listen(ImageContentBlock, 'before_update', update_timestamps_before_update)

event.listen(ImageContentBlock, 'before_insert', update_confirmedat_before_save)
event.listen(ImageContentBlock, 'before_update', update_confirmedat_before_save)

event.listen(ImageContentBlock, 'before_insert', update_slug_before_save)
event.listen(ImageContentBlock, 'before_update', update_slug_before_save)
