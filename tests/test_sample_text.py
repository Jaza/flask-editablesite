# -*- coding: utf-8 -*-
"""Test the sample text generation."""

import pytest

from flask_editablesite.app import create_app
from flask_editablesite.settings import TestConfig


from flask_editablesite.editable.sample_text import (
    placeholder_or_random_sample_text,)


def test_placeholder_when_no_scrape_configured(app):
    sample_text = placeholder_or_random_sample_text()
    assert sample_text == app.config['EDITABLE_PLACEHOLDER_TEXT']


class TextScrapeTestConfig(TestConfig):
    EDITABLE_SAMPLE_TEXT_SCRAPE_URLS = [
        (
            'https://raw.githubusercontent.com'
            '/Jaza/flask-editablesite'
            '/master/tests/sample-text-great-expectations.txt'),]


def test_markovify_when_scrape_configured():
    app = create_app(TextScrapeTestConfig)

    with app.app_context():
        sample_text = placeholder_or_random_sample_text()

        assert sample_text is not None
        assert len(sample_text)
        assert sample_text != app.config['EDITABLE_PLACEHOLDER_TEXT']

        assert (
            ('and' in sample_text)
            or ('the' in sample_text)
            or ('that' in sample_text)
            or ('you' in sample_text)
            or ('man' in sample_text)
            or ('was' in sample_text)
            or ('with' in sample_text)
            or ('said' in sample_text)
            or ('him' in sample_text)
            or ('were' in sample_text))
