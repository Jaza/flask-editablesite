# -*- coding: utf-8 -*-
"""Test that content blocks show as expected."""

import pytest


def test_home_textcontentblock_default_content_visible(db, testapp):
    from flask_editablesite.contentblock.models import (
        ShortTextContentBlock, RichTextContentBlock)

    default_content = ShortTextContentBlock.default_content()
    default_content.update(
        RichTextContentBlock.default_content())

    res = testapp.get("/")

    for o in default_content.values():
        assert o.content in res.text
