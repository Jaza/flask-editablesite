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

This project is still **under active development**. I hope to have it mainly finished within the next week or so (as of 14 Oct 2015).

The aim of this app is to demonstrate that, with the help of modern JS libraries, and with some well-thought-out server-side snippets, it's now perfectly possible to "bake in" live in-place editing for virtually every content element in a typical brochureware site.

This app is not a CMS. On the contrary, think of it as a proof-of-concept alternative to a CMS. An alternative where there's no "admin area", there's no "editing mode", and there's no "preview button". There's only direct manipulation.

"Template" means that this is a sample app. It comes with a bunch of models that work out-of-the-box (e.g. text content block, image content block, gallery item, event). However, these are just a starting point: you can and should define your own models when building a real site. Same with the front-end templates: the home page layout and the CSS styles are just examples.


Quickstart
----------

First, set your app's secret key as an environment variable. For example, add the following to ``.bashrc`` or ``.bash_profile``.

.. code-block:: bash

    export FLASK_EDITABLESITE_SECRET='something-really-secret'


Then run the following commands to bootstrap your environment.


::

    git clone https://github.com/Jaza/flask-editablesite
    cd flask-editablesite
    pip install -r requirements/dev.txt
    python manage.py server

You will see a pretty welcome screen.

Once you have installed your DBMS, run the following to create your app's database tables and perform the initial migration:

::

    python manage.py db init
    python manage.py db migrate
    python manage.py db upgrade
    python manage.py server


Dynamic Secret Key
------------------

You can have a different random secret key each time the app starts,
if you want:

::

    export FLASK_EDITABLESITE_SECRET=`python -c "import os; from binascii import hexlify; print(hexlify(os.urandom(24)))"`; python manage.py server


Specifying DB config
--------------------

You must specify the DB credentials before starting the app in normal mode:

::

    export FLASK_EDITABLESITE_DATABASE_URI="postgresql://flask_editablesite:flask_editablesite@localhost:5432/flask_editablesite"


Session store mode
------------------

The app can be configured to store all content as session data, instead of saving it to the database. To do this, set the following environment variable:

::

    export FLASK_EDITABLESITE_USE_SESSIONSTORE_NOT_DB=1

When in session store mode, all content changes are lost whenever a new session is started (e.g. if the user clears his/her cookies, or switches to a different browser). A user's edits are only visible to him/her self, not to anyone else. Session store mode is therefore very useful for running the app in a demo or test environment. It should **not** be used in production, where you want content edits to actually be persisted and shown to other users!

If session store mode is enabled, the app doesn't need a database at all (i.e. you don't even need to configure DB credentials).

Also, if session store mode is enabled, then it's highly recommended that you store session data server-side. For this purpose, the app comes with `Flask-Session <http://pythonhosted.org/Flask-Session/>`_ installed. If you leave session storage as Flask's default (i.e. store client-side in a cookie), then you'll soon find your content disappearing (or errors being thrown), because no more than 4KB of data can be stored in one cookie.

For example, to store session data on the filesystem:

::

    export FLASK_EDITABLESITE_SESSION_TYPE="filesystem"
    export FLASK_EDITABLESITE_SESSION_FILE_DIR="static/cache/sessions"

Or, to store it in Memcached:

::

    export FLASK_EDITABLESITE_SESSION_TYPE="memcached"
    export FLASK_EDITABLESITE_SESSION_MEMCACHED="your.memcached.host:11211"


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


Migrations
----------

Whenever a database migration needs to be made. Run the following commands:
::

    python manage.py db migrate

This will generate a new migration script. Then run:
::

    python manage.py db upgrade

To apply the migration.

For a full migration command reference, run ``python manage.py db --help``.
