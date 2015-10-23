# -*- coding: utf-8 -*-
"""Test the sample image selection."""

import os

from flask_editablesite.app import create_app
from flask_editablesite.settings import TestConfig


from flask_editablesite.editable.sample_images import (
    placeholder_or_random_sample_image,)


def test_placeholder_when_no_sample_images_configured(app):
    sample_image = placeholder_or_random_sample_image()
    assert sample_image == app.config[
        'EDITABLE_PLACEHOLDER_IMAGE_RELATIVE_PATH']


class ImageScrapeTestConfig(TestConfig):
    EDITABLE_SAMPLE_IMAGES_SCRAPE_URL = (
        'http://www.psych.usyd.edu.au/pdp-11/Images/Images.html')
    EDITABLE_SAMPLE_IMAGES_SCRAPE_PARENTELNAME = 'li'
    EDITABLE_SAMPLE_IMAGES_RELATIVE_PATH = 'pdp11/'


def test_sample_image_when_scrape_configured():
    app = create_app(ImageScrapeTestConfig)

    with app.app_context():
        sample_image = placeholder_or_random_sample_image()

        assert sample_image is not None
        assert len(sample_image)
        assert sample_image != app.config[
            'EDITABLE_PLACEHOLDER_IMAGE_RELATIVE_PATH']

        sample_image_filepath = os.path.abspath(os.path.join(
            app.config['MEDIA_FOLDER'],
            sample_image))

        assert os.path.exists(sample_image_filepath)
        os.remove(sample_image_filepath)
