from bs4 import BeautifulSoup
import os
import random
import requests

try:
    from urllib.parse import urlparse  # python 3.x
except ImportError:
    from urlparse import urlparse  # python 2.x

from flask import current_app as app


def scrape_sample_images(url, parentelname=None, parentelclass=None,
                         onlyfirstel=False):
    """Scrapes the given URL for sample image links."""

    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    hrefs = []

    if parentelname:
        soup_kwargs = {}

        if parentelclass:
            soup_kwargs['class_'] = parentelclass

        for parent_el in soup.find_all(parentelname, **soup_kwargs):
            if onlyfirstel:
                link = next(iter(parent_el.find_all('a'))).get('href')
                hrefs.append(link)
            else:
                for link in parent_el.find_all('a'):
                    hrefs.append(link.get('href'))
    else:
        for link in soup.find_all('a'):
            hrefs.append(link.get('href'))

    return hrefs


def placeholder_or_random_sample_image():
    """
    Gets a random sample image if possible, otherwise the default
    placeholder image.
    """

    is_sample_images_configured = (
        app.config.get('EDITABLE_SAMPLE_IMAGES_SCRAPE_URL') and
        app.config.get('EDITABLE_SAMPLE_IMAGES_RELATIVE_PATH'))

    return (is_sample_images_configured
            and random_sample_image()
            or app.config['EDITABLE_PLACEHOLDER_IMAGE_RELATIVE_PATH'])


def random_sample_image():
    """Attempts to get a random sample image."""

    hrefs = scrape_sample_images(
        url=app.config['EDITABLE_SAMPLE_IMAGES_SCRAPE_URL'],
        parentelname=app.config.get(
            'EDITABLE_SAMPLE_IMAGES_SCRAPE_PARENTELNAME'),
        parentelclass=app.config.get(
            'EDITABLE_SAMPLE_IMAGES_SCRAPE_PARENTELCLASS'),
        onlyfirstel=app.config.get(
            'EDITABLE_SAMPLE_IMAGES_SCRAPE_ONLYFIRSTEL'))

    if not hrefs:
        return None

    href = random.choice(hrefs)

    targetdir = os.path.abspath(os.path.join(
        app.config['MEDIA_FOLDER'],
        app.config['EDITABLE_SAMPLE_IMAGES_RELATIVE_PATH']))
    target_filepath = os.path.abspath(targetdir)

    if not os.path.exists(target_filepath):
        os.makedirs(target_filepath)

    filename = os.path.basename(urlparse(href).path)
    filepath = os.path.join(target_filepath, filename)

    if not os.path.exists(filepath):
        r = requests.get(href, stream=True)

        with open(filepath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

    return os.path.join(
        app.config['EDITABLE_SAMPLE_IMAGES_RELATIVE_PATH'],
        filename)
