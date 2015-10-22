# -*- coding: utf-8 -*-
"""Test that content blocks show as expected."""

import pytest

from flask import url_for

from flask_editablesite.extensions import thumb
from flask_editablesite.contentblock.models import (
    ShortTextContentBlock, RichTextContentBlock)


def test_home_textcontentblock_default_content_visible(db, testapp):
    default_content = ShortTextContentBlock.default_content()
    default_content.update(
        RichTextContentBlock.default_content())

    res = testapp.get("/")

    for o in default_content.values():
        assert o.content in res.text


def test_home_imagecontentblock_default_site_logo_visible(app, db,
                                                          testapp):
    res = testapp.get("/")

    assert (
        (
            '<img class="img-responsive img-circle img-lesswidth" '
            'src="{0}" alt="{1}">').format(
                url_for('static', filename=thumb.thumbnail(
                    app.config[
                        'EDITABLE_PLACEHOLDER_IMAGE_RELATIVE_PATH'],
                    size='256x256',
                    crop='fit')),
                app.config['SITE_NAME'])
        in res.text)
