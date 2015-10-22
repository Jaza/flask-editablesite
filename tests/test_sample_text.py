# -*- coding: utf-8 -*-
"""Test the sample text generation."""

import pytest

from flask_editablesite.app import create_app


from flask_editablesite.editable.sample_text import (
    placeholder_or_random_sample_text,)


def test_placeholder_when_no_scrape_configured(app):
    sample_text = placeholder_or_random_sample_text()
    assert sample_text == app.config['EDITABLE_PLACEHOLDER_TEXT']
