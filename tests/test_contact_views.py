# -*- coding: utf-8 -*-
"""Test using the contact form."""

import pytest


def test_contactform_alert_visible(db, testapp):
    # Goes to homepage
    res = testapp.get("/")
    # Fills out contact form
    form = res.forms['contactForm']
    form['name'] = 'John Smith'
    form['email'] = 'john@smith.com'
    form['phone'] = '0404123456'
    form['message'] = 'Hi there! How are you?'
    # Submits
    res = form.submit().follow()
    assert res.status_code == 200
    assert 'Your message has been sent.' in res
