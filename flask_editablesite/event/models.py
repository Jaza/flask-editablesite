# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
import random
import string

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


class Event(SurrogatePK, Slugged, TimeStamped, Confirmable, Model):
    __tablename__ = 'event'

    start_date = Column(db.Date(), nullable=False)
    end_date = Column(db.Date())
    start_time = Column(db.Time())
    end_time = Column(db.Time())
    event_url = Column(db.String(255), nullable=False, default='')
    location_name = Column(db.String(255), nullable=False, default='')
    location_url = Column(db.String(255), nullable=False, default='')

    __table_args__ = (
        db.UniqueConstraint('slug', name='_event_slug_uc'),
        db.Index('_event_active_startdate_ix', 'active', 'start_date'))

    def __repr__(self):
        return self.title

    @classmethod
    def new_item(cls, title_prefix='New ', rand_start_date=False):
        rand_str = ''.join(
            random.choice(string.ascii_lowercase) for _ in range(10))
        title = '{0}Event {1}'.format(title_prefix, rand_str)
        slug = slugify(title, to_lower=True)

        # Make start date a random date within 5 years of today
        date_now = date.today()
        start_date = date_now

        if rand_start_date:
            fiveyears_indays = 365 * 5
            rand_delta = timedelta(
                days=random.randrange(
                    -fiveyears_indays, fiveyears_indays))
            start_date += rand_delta

        start_time = None
        # Toss a coin to see if we set a start time or not
        if bool(random.getrandbits(1)):
            rand_delta = timedelta(minutes=(15 * random.randrange(96)))
            dt_now = datetime.now()
            dt_midnighttoday = datetime(dt_now.year, dt_now.month, dt_now.day)
            start_time = (dt_midnighttoday + rand_delta).time()

        end_date = None
        end_time = None
        # Toss a coin to see if we set an end date or not
        if bool(random.getrandbits(1)):
            # Make end date 5 days or less ahead of start date
            rand_delta = timedelta(days=random.randrange(1, 6))
            end_date = start_date + rand_delta

            # Toss a coin to see if we set an end time or not
            if bool(random.getrandbits(1)):
                rand_delta = timedelta(minutes=(15 * random.randrange(96)))
                dt_now = datetime.now()
                dt_midnighttoday = datetime(
                    dt_now.year, dt_now.month, dt_now.day)
                end_time = (dt_midnighttoday + rand_delta).time()

        # Toss a coin to see if we set an event URL or not
        event_url = ''
        if bool(random.getrandbits(1)):
            event_url = random.choice(app.config['EDITABLE_SAMPLE_URLS'])

        # Toss a coin to see if we set a location name or not
        location_name = ''
        location_url = ''
        if bool(random.getrandbits(1)):
            rand_str = ''.join(
                random.choice(string.ascii_lowercase)
                for _ in range(10))
            location_name = 'Location {0}'.format(rand_str)

            # Toss a coin to see if we set a location URL or not
            if bool(random.getrandbits(1)):
                location_url = random.choice(
                    app.config['EDITABLE_SAMPLE_URLS'])

        return cls(
            title=title,
            slug=slug,
            start_date=start_date,
            end_date=end_date,
            start_time=start_time,
            end_time=end_time,
            event_url=event_url,
            location_name=location_name,
            location_url=location_url,
            active=True)

    @classmethod
    def default_content(cls):
        return [
            cls.new_item(title_prefix='Sample ', rand_start_date=True)
            for i in range(app.config['EVENT_NUM_DEFAULT_ITEMS'])]


event.listen(Event, 'before_insert', update_timestamps_before_insert)
event.listen(Event, 'before_update', update_timestamps_before_update)

event.listen(Event, 'before_insert', update_confirmedat_before_save)
event.listen(Event, 'before_update', update_confirmedat_before_save)

event.listen(Event, 'before_insert', update_slug_before_save)
event.listen(Event, 'before_update', update_slug_before_save)
