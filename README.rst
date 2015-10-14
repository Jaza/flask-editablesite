Flask Editable Site
===================

A template for building a small marketing web site in `Flask
<http://flask.pocoo.org/>`_ where all content is live editable.

This app includes front- and back-end utilites for live / in-place editing of several different field types:

- **Short text:** a regular text field with (AJAX-based) auto-save
- **Rich text:** a ``textarea`` converted to WYSIWYG (powered by `Dante <http://michelson.github.io/Dante/>`_) with auto-save
- **Image:** a file field converted to a drag-and-drop live image upload widget (powered by `Dropzone.js <http://www.dropzonejs.com/>`_)
- **Date/time:** a regular text field converted to a date/time picker with auto-save

It also includes utilities for adding to, re-ordering, and deleting from lists of content items.

Here's a `demo of the app in action
<https://flask-editablesite.herokuapp.com/>`_.

This project is still **under active development**. I hope to have it mainly finished within the next week or so (as of 14 Oct 2015).

The aim of this app is to demonstrate that, with the help of modern JS libraries, and with some well-thought-out server-side snippets, it's now perfectly possible to "bake in" live in-place editing for virtually every content element in a typical brochureware site.

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

You can specify DB config when the app starts:

::

    export FLASK_EDITABLESITE_DATABASE_URI="postgresql://flask_editablesite:flask_editablesite@localhost:5432/flask_editablesite"; python manage.py server


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
