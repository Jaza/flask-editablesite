# -*- coding: utf-8 -*-
from datetime import date
import random
import string

from sqlalchemy import event, func
from slugify import slugify

from flask import current_app as app
from flask import url_for

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


class GalleryItem(SurrogatePK, Slugged, TimeStamped,
                  Confirmable, Model):
    __tablename__ = 'gallery_item'

    image = Column(db.String(255), nullable=False, default='')
    content = Column(db.Text(), nullable=False, default='')
    date_taken = Column(db.String(255), nullable=False, default='')
    weight = db.Column(db.Integer(), nullable=False, default=0)

    __table_args__ = (
        db.UniqueConstraint('slug', name='_gi_slug_uc'),
        db.Index('_gi_slug_active_ix', 'slug', 'active'))

    def __repr__(self):
        return self.title

    @property
    def image_path(self):
        return (
            self.image
            and '%s%s' % (
                app.config['UPLOADS_RELATIVE_PATH'], self.image)
            or None)

    @property
    def image_url(self):
        if not self.image:
            return None

        return url_for('static', filename=self.image_path,
                       _external=True)

    @property
    def image_or_placeholder(self):
        return (
            self.image
            or app.config['EDITABLE_PLACEHOLDER_IMAGE_RELATIVE_PATH'])

    @classmethod
    def new_item(cls, title_prefix='New '):
        rand_str = ''.join(
            random.choice(string.ascii_lowercase) for _ in range(10))
        title = '{0}Gallery Item {1}'.format(title_prefix, rand_str)
        slug = slugify(title, to_lower=True)

        year_now = date.today().year
        date_taken = '{0} {1}'.format(
            random.choice(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']),
            random.choice([(year_now - x) for x in range(1, 11)]))

        return cls(
            title=title,
            slug=slug,
            image=app.config[
                'EDITABLE_PLACEHOLDER_IMAGE_RELATIVE_PATH'],
            date_taken=date_taken,
            content=app.config['EDITABLE_PLACEHOLDER_TEXT'],
            active=True)

    @classmethod
    def default_content(cls):
        ret = []

        for i in range(app.config['GALLERY_NUM_DEFAULT_ITEMS']):
            item = cls.new_item(title_prefix='Sample ')
            item.weight = i

            ret.append(item)

        return ret

    @classmethod
    def max_weight(cls):
        result = (cls.query
                     .with_entities(
                         func.max(cls.weight).label('max_weight'))
                     .first())

        if not (
                result and
                (type(result).__name__ in ('KeyedTuple', 'result')) and
                len(result) and
                result[0] is not None):
            return None

        return int(result[0])


event.listen(GalleryItem, 'before_insert',
             update_timestamps_before_insert)
event.listen(GalleryItem, 'before_update',
             update_timestamps_before_update)

event.listen(GalleryItem, 'before_insert',
             update_confirmedat_before_save)
event.listen(GalleryItem, 'before_update',
             update_confirmedat_before_save)

event.listen(GalleryItem, 'before_insert', update_slug_before_save)
event.listen(GalleryItem, 'before_update', update_slug_before_save)
