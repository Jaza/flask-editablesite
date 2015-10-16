# -*- coding: utf-8 -*-
from sqlalchemy import event, func

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


event.listen(Event, 'before_insert', update_timestamps_before_insert)
event.listen(Event, 'before_update', update_timestamps_before_update)

event.listen(Event, 'before_insert', update_confirmedat_before_save)
event.listen(Event, 'before_update', update_confirmedat_before_save)

event.listen(Event, 'before_insert', update_slug_before_save)
event.listen(Event, 'before_update', update_slug_before_save)
