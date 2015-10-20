# -*- coding: utf-8 -*-

import markovify
import random
import requests
from unidecode import unidecode

from flask import current_app as app
from flask import g


def placeholder_or_random_sample_text():
    """
    Gets a random sample chunk of text if possible, otherwise the
    default placeholder text.
    """

    is_sample_text_configured = (
        app.config.get('EDITABLE_SAMPLE_TEXT_SCRAPE_URLS') and
        True or False)

    return (is_sample_text_configured
            and random_sample_text()
            or app.config['EDITABLE_PLACEHOLDER_TEXT'])


def random_sample_text(num_sentences=3):
    """Attempts to generate a random piece of text content."""

    text = getattr(g, 'sample_text_cached', None)

    if not text:
        url = random.choice(
            app.config['EDITABLE_SAMPLE_TEXT_SCRAPE_URLS'])

        r = requests.get(url)

        # Thanks to:
        # https://github.com/kennethreitz/requests/issues/1604 ...
        # #issuecomment-24476927
        r.encoding = 'utf-8'

        text = r.text.encode('utf-8')
        g.sample_text_cached = text

    # Use a Markov chain generator for random sentences based on
    # sample input (e.g. text of a book).
    # https://github.com/jsvine/markovify
    # See also:
    # http://agiliq.com/blog/2009/06/ ...
    # generating-pseudo-random-text-with-markov-chains-u/
    text_model = markovify.Text(text)

    return '<p>{0}</p>'.format(' '.join([
        unidecode(text_model
                  .make_sentence().decode('utf-8').strip())
        for i in range(num_sentences)]))
