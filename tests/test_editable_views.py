# -*- coding: utf-8 -*-
"""Test editable view routes."""

import pytest

from flask_editablesite.contentblock.models import (
    ShortTextContentBlock,)


def test_home_textcontentblock_update_visible(app, user, testapp):
    # Goes to homepage
    res = testapp.get("/")
    # Fills out login form
    form = res.forms['loginForm']
    form['email'] = user.email
    form['password'] = 'myprecious'
    # Submits
    res = form.submit().follow()

    default_content = ShortTextContentBlock.default_content()
    assert default_content['site-byline'].content in res

    form = res.forms[
        'short-text-form-short_text_content_block-content-site-byline']
    new_byline = 'This is a rather mediocre byline.'
    form['content'] = new_byline

    res = form.submit().follow()
    assert new_byline in res
    assert not(default_content['site-byline'].content in res)
