import importlib
import os
import random
import re
import requests
from urlparse import urlparse

from flask import current_app as app

from flask_editablesite.editable.sample_images import scrape_sample_images


def get_model_class(model_classpath, model_name):
    """Dynamically imports the model with the specified classpath."""

    model_classpath_format = r'^[a-z0-9_]+(\.[A-Za-z0-9_]+)+$'

    if not re.match(model_classpath_format, model_classpath):
        raise ValueError('Class path "%s" for model name "%s" must be a valid Python module / class path (in the format "%s")' % (model_classpath, model_name, model_classpath_format))

    model_classpath_split = model_classpath.rpartition('.')
    model_modulepath, model_classname = (model_classpath_split[0], model_classpath_split[2])

    try:
        model_module = importlib.import_module(model_modulepath)
    except ImportError:
        raise ValueError('Error importing module "%s" for model name "%s"' % (model_modulepath, model_name))

    model_class = getattr(model_module, model_classname, None)
    if not model_class:
        raise ValueError('Class "%s" not found in module "%s" for model name "%s"' % (model_classname, model_modulepath, model_name))

    return model_class


def placeholder_or_random_sample_image():
    """Gets a random sample image if possible, otherwise the default placeholder image."""

    is_sample_images_configured = (
        app.config.get('EDITABLE_SAMPLE_IMAGES_SCRAPE_URL') and
        app.config.get('EDITABLE_SAMPLE_IMAGES_RELATIVE_PATH'))

    return (is_sample_images_configured
        and random_sample_image()
        or app.config['EDITABLE_PLACEHOLDER_IMAGE_RELATIVE_PATH'])


def random_sample_image():
    """Attempts to get a random sample image."""

    try:
        hrefs = scrape_sample_images(
            url=app.config['EDITABLE_SAMPLE_IMAGES_SCRAPE_URL'],
            parentelname=app.config.get('EDITABLE_SAMPLE_IMAGES_SCRAPE_PARENTELNAME'),
            parentelclass=app.config.get('EDITABLE_SAMPLE_IMAGES_SCRAPE_PARENTELCLASS'),
            onlyfirstel=app.config.get('EDITABLE_SAMPLE_IMAGES_SCRAPE_ONLYFIRSTEL'))
    except Exception:
        return None

    if not hrefs:
        return None

    href = random.choice(hrefs)

    targetdir = os.path.abspath(os.path.join(app.config['MEDIA_FOLDER'], app.config['EDITABLE_SAMPLE_IMAGES_RELATIVE_PATH']))
    target_filepath = os.path.abspath(targetdir)

    try:
        if not os.path.exists(target_filepath):
            os.makedirs(target_filepath)
    except OSError:
        return None

    filename = os.path.basename(urlparse(href).path)
    filepath = os.path.join(target_filepath, filename)

    if not os.path.exists(filepath):
        try:
            r = requests.get(href, stream=True)

            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
        except Exception:
            return None

    return os.path.join(
        app.config['EDITABLE_SAMPLE_IMAGES_RELATIVE_PATH'],
        filename)
