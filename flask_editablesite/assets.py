# -*- coding: utf-8 -*-
from flask_assets import Bundle, Environment

css = Bundle(
    "libs/bootstrap/dist/css/bootstrap.css",
    "css/style.css",
    filters="cssmin",
    output="public/css/common.css"
)

css_admin = Bundle(
    "libs/Dante/css/dante-editor.css",
    "css/editable.css",
    filters='cssmin',
    output='public/css/admin.css'
)

js = Bundle(
    "libs/jQuery/dist/jquery.js",
    "libs/bootstrap/dist/js/bootstrap.min.js",
    filters='jsmin',
    output="public/js/common.js"
)

js_admin = Bundle(
    "libs/underscore/js/underscore-min.js",
    "libs/moment/moment.min.js",
    "libs/bootbox/js/bootbox.min.js",
    "libs/bootstrap-datetimepicker/js/bootstrap-datetimepicker.js",
    "libs/Sanitize.js/js/sanitize.js",
    "libs/Dante/js/dante-editor.js",
    "js/autosave.js",
    "js/editable.js",
    "js/dante.js",
    filters='jsmin',
    output='public/js/admin.js'
)

assets = Environment()

assets.register("js_all", js)
assets.register("css_all", css)

assets.register("js_admin", js_admin)
assets.register("css_admin", css_admin)
