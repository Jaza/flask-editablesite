Flask Editable Site
===================

A template for building a small marketing web site in `Flask
<http://flask.pocoo.org/>`_ where all content is live editable.

This app includes front- and back-end utilites for live / in-place editing of several different field types:

- **Short text:** a regular text field with (AJAX-based) auto-save
- **Rich text:** a ``textarea`` converted to WYSIWYG (powered by `Dante <http://michelson.github.io/Dante/>`_) with auto-save
- **Image:** a file field converted to a drag-and-drop live image upload widget (powered by `Dropzone.js <http://www.dropzonejs.com/>`_)
- **Date/time:** a regular text field converted to a date/time picker with auto-save

It also includes utilities for adding to, re-ordering, and deleting from lists of content items (all via in-place editing).

Here's a `demo of the app in action
<https://flask-editablesite.herokuapp.com/>`_.

The aim of this app is to demonstrate that, with the help of modern JS libraries, and with some well-thought-out server-side snippets, it's now perfectly possible to "bake in" live in-place editing for virtually every content element in a typical brochureware site.

This app is not a CMS. On the contrary, think of it as a proof-of-concept alternative to a CMS. An alternative where there's no "admin area", there's no "editing mode", and there's no "preview button". There's only direct manipulation.

"Template" means that this is a sample app. It comes with a bunch of models that work out-of-the-box (e.g. text content block, image content block, gallery item, event). However, these are just a starting point: you can and should define your own models when building a real site. Same with the front-end templates: the home page layout and the CSS styles are just examples.

|build-status| |coverage|

.. |build-status| image:: https://travis-ci.org/Jaza/flask-editablesite.svg?branch=master
   :target: https://travis-ci.org/Jaza/flask-editablesite
   :alt: Travis CI status

.. |coverage| image:: https://coveralls.io/repos/Jaza/flask-editablesite/badge.svg?branch=master
   :target: https://coveralls.io/r/Jaza/flask-editablesite
   :alt: Coverage status


Quickstart
----------

First, set your app's secret key as an environment variable. For example, add the following to ``.bashrc`` or ``.bash_profile`` ::

    export FLASK_EDITABLESITE_SECRET='something-really-secret'

Then run the following commands to bootstrap your environment ::

    git clone https://github.com/Jaza/flask-editablesite
    cd flask-editablesite
    pip install -r requirements/dev.txt

Before running the app, you'll need to either specify DB config, or enable session store mode. See instructions further down for details on either of these. Then you can run the app with this command ::

    python manage.py server

You will see a pretty welcome screen.


Dynamic Secret Key
------------------

You can have a different random secret key each time the app starts,
if you want ::

    export FLASK_EDITABLESITE_SECRET=`python -c "import os; from binascii import hexlify; print(hexlify(os.urandom(24)))"`; python manage.py server


DB config and migrations
------------------------

You must specify the DB credentials before starting the app in normal mode ::

    export FLASK_EDITABLESITE_DATABASE_URI="postgresql://flask_editablesite:flask_editablesite@localhost:5432/flask_editablesite"

If using your own DB models, run the following to get started with migrations ::

    python manage.py db init

Each time you need to create a new migration script, run the following ::

    python manage.py db migrate

If using the included sample models and migrations, or if you've already initialised and created migrations for your own models, then run the following to create the DB schema ::

    python manage.py db upgrade

For a full migration command reference, run ``python manage.py db --help``.


Session store mode
------------------

The app can be configured to store all content as session data, instead of saving it to the database. To do this, set the following environment variable ::

    export FLASK_EDITABLESITE_USE_SESSIONSTORE_NOT_DB=1

When in session store mode, all content changes are lost whenever a new session is started (e.g. if the user clears his/her cookies, or switches to a different browser). A user's edits are only visible to him/her self, not to anyone else. Session store mode is therefore very useful for running the app in a demo or test environment. It should **not** be used in production, where you want content edits to actually be persisted and shown to other users!

If session store mode is enabled, the app doesn't need a database at all (i.e. you don't even need to configure DB credentials).

Also, if session store mode is enabled, then it's highly recommended that you store session data server-side. For this purpose, the app comes with `Flask-Session <http://pythonhosted.org/Flask-Session/>`_ installed. If you leave session storage as Flask's default (i.e. store client-side in a cookie), then you'll soon find your content disappearing (or errors being thrown), because `no more than 4KB of data can be stored in one cookie <http://greenash.net.au/thoughts/2015/10/cookies-cant-be-more-than-4kib-in-size/>`_.

For example, to store session data on the filesystem ::

    export FLASK_EDITABLESITE_SESSION_TYPE="filesystem"
    export FLASK_EDITABLESITE_SESSION_FILE_DIR="static/cache/sessions"

Or, to store it in Memcached ::

    export FLASK_EDITABLESITE_SESSION_TYPE="memcached"
    export FLASK_EDITABLESITE_SESSION_MEMCACHED="your.memcached.host:11211"


Creating users
--------------

When in normal (DB) mode, you'll need to create a user in order to log in and start editing. For the sake of simplicity, and in order to maintain the "no admin area" ideal, this app doesn't include any GUI for creating or managing users. If you need a GUI for user management, or for anything else, there are plenty of Flask packages that can help you out, with the best candidate being `Flask-Admin <https://flask-admin.readthedocs.org/>`_.

To create a user, run this command ::

    python manage.py createuser

And enter an email and password when prompted. You will then be able to log in. Also, again for simplicity, this app doesn't include any definition or management of user roles: if a user exists and is active, then he/she can log in and edit everything, end of story. For many small sites, this is all that's needed anyway.

When in session store mode, the app makes one user account available for login purposes. The default email and password for this user is ``test@test.com`` and ``test``, respectively. You can override these by setting the ``FLASK_EDITABLESITE_SESSIONSTORE_USER_EMAIL`` and ``FLASK_EDITABLESITE_SESSIONSTORE_USER_PASSWORD`` environment variables. The login email and password are shown on the home page when logged out, so that users demo'ing the app have easy access to the credentials.


Sample content
--------------

The app comes with some utilities for populating a site with random text and images (from configured sources). This works either in regular (database) mode, or in session store mode. It's handy for demo, prototyping, and "placeholder content" purposes.

For the "sample images" functionality, you can configure the app to scrape links to images from a URL of your choice. E.g. say the web site ``coolexamplephotos.com`` has source code that looks something like this ::

    <html>
    <head>
      <title>Cool Example Photos</title>
    </head>
    <body>
      <h1>Cool Example Photos</h1>

      <ul>
        <li><a href="http://coolexamplephotos.com/photos/foo.jpg">foo.jpg</a></li>
        <li><a href="http://coolexamplephotos.com/photos/bar.jpg">bar.jpg</a></li>
        <li><a href="http://coolexamplephotos.com/photos/baz.jpg">baz.jpg</a></li>
      </ul>
    </body>
    </html>

Set the following environment variables, and the app will randomly source images from that site and display them in image fields ::

    export FLASK_EDITABLESITE_EDITABLE_SAMPLE_IMAGES_SCRAPE_URL="http://coolexamplephotos.com/"
    export FLASK_EDITABLESITE_EDITABLE_SAMPLE_IMAGES_SCRAPE_PARENTELNAME="li"
    export FLASK_EDITABLESITE_EDITABLE_SAMPLE_IMAGES_RELATIVE_PATH="coolexamplephotos/"

Where ``FLASK_EDITABLESITE_EDITABLE_SAMPLE_IMAGES_SCRAPE_URL`` is the URL of the page to scrape, ``FLASK_EDITABLESITE_EDITABLE_SAMPLE_IMAGES_SCRAPE_PARENTELNAME`` is the parent element of the image links, and ``FLASK_EDITABLESITE_EDITABLE_SAMPLE_IMAGES_RELATIVE_PATH`` is the relative directory in which to store the downloaded images on the filesystem.

To pre-download the sample images for faster access, use the ``downloadsampleimages`` command like so ::

    python manage.py downloadsampleimages --url="http://coolexamplephotos.com/" --targetdir=./flask_editablesite/static/uploads/coolexamplephotos --parentelname="li"

For the "sample text" functionality, you can configure one or more URLs of texts to use as source material. The texts can be anything (e.g. "lorem ipsum" blurb, blog posts, encyclopaedia entries), and can be in any text format (e.g. HTML, RSS, CSV); but books in plain text are recommended.

Set the following environment variable to randomly source text from one of the URLs ::

    export FLASK_EDITABLESITE_EDITABLE_SAMPLE_TEXT_SCRAPE_URLS="['http://cooltextsources.com/texts/foo.txt', 'http://cooltextsources.com/texts/bar.txt', 'http://cooltextsources.com/texts/baz.txt']"

The actual sentences that then get displayed in text fields, are generated based on the chosen source text, using the `Markovify <https://github.com/jsvine/markovify>`_ library.

If using sample images and/or text with these utilities, it's recommended to set the "credits" environment variables, which will show your specified acknowledgements on the home page ::

    export FLASK_EDITABLESITE_EDITABLE_SAMPLE_IMAGES_CREDITS='<p>The placeholder images are a selection from the public domain <a href="http://coolexamplephotos.com/">Cool Example Photos</a> photo collection (a different random set for each session). Many thanks to John Smith of Foobar Design.</p>'
    export FLASK_EDITABLESITE_EDITABLE_SAMPLE_TEXT_CREDITS='<p>The placeholder text is sourced from a subset of the public domain <a href="http://cooltextsources.org/">Cool Text Sources</a> texts collection (a different random text for each session). Many thanks to the original text authors. The actual sentences in the text are generated using the <a href="https://github.com/jsvine/markovify">Markovify</a> library.</p>'


Deployment
----------

In your production environment, make sure the ``FLASK_EDITABLESITE_ENV`` environment variable is set to ``"prod"``.


Shell
-----

To open the interactive shell, run ::

    python manage.py shell

By default, you will have access to ``app``, ``db``, and the ``User`` model.


Running Tests
-------------

To run all tests, run ::

    python manage.py test
