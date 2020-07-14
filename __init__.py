# -*- coding: utf-8 -*-

"""This file contains initialization code."""

import os

from elasticsearch import Elasticsearch
from celery import Celery
from babel import dates as babel_dates
from flask import Flask, render_template, request
from flask_assets import Environment, Bundle
from flask_babel import Babel, _
from flask_mail import Mail
from flask_migrate import Migrate
from flask_misaka import Misaka
from flask_sqlalchemy import SQLAlchemy
from flask_user import SQLAlchemyAdapter, UserManager, current_user
# from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect


import flask
import pytz
import webassets

from cyber_role.bootstrap import BASE_CONFIG, LANGUAGES, HashidsWrapper,CeleryWrapper
from cyber_role.errors import forbidden, page_not_found, server_error

__version__ = '0.1.0'



def make_celery(app):
    celery = Celery(
        app.import_name,
        backend="redis://localhost:6379/0",
        broker="redis://localhost:6379/1"
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

# Hashids
hashids_hasher = HashidsWrapper()


# Babel
babel = Babel()

# CSRF
csrf = CSRFProtect()

# SQLAlchemy
db = SQLAlchemy()

#Celery
celery = Celery(__name__, broker=bootstrap.CELERY_BROKER_URL,backend=bootstrap.CELERY_RESULT_BACKEND)

# Flask-Migrate
migrate = Migrate()

# Flask-Mail
mail = Mail()

# Flask-User
user_manager = UserManager()

# Flask-Login
# login_manager = LoginManager()

# Flask-Misaka
md = Misaka(
    fenced_code=False,
    underline=True,
    no_intra_emphasis=False,
    strikethrough=True,
    superscript=True,
    tables=True,
    no_html=True,
    escape=True
)

# Flask-Assets
assets = Environment()


@babel.localeselector
def get_locale():
    """Get locale from user record or from browser locale."""
    if not current_user or not current_user.is_authenticated:
        # Not logged in user
        return request.accept_languages.best_match(LANGUAGES)

    return current_user.locale


def url_for_self(**kwargs):
    """Helper to return current endpoint in Jinja template."""
    return flask.url_for(
        flask.request.endpoint,
        **dict(flask.request.view_args, **kwargs)
    )


def format_datetime(value):
    """Jinja filter to format datetime using user defined timezone.

    If not a valid timezone, defaults to UTC.

    Args:
        value (datetime): Datetime object to represent.
    """
    user_tz = current_user.timezone

    if not user_tz or user_tz not in pytz.common_timezones:
        user_tz = 'UTC'

    tz = babel_dates.get_timezone(user_tz)

    return babel_dates.format_datetime(
        value,
        'yyyy-MM-dd HH:mm:ss',
        tzinfo=tz
    )


def init_app():
    """Initialize app."""
    app = Flask(__name__)
    
    app.config.update(BASE_CONFIG)

    # Load configuration specified in environment variable or default
    # development one.
    # Production configurations shold be stored in a separate directory, such
    # as `instance`.
    if 'FLASK_APP_CONFIG' in os.environ:
        app.config.from_envvar('FLASK_APP_CONFIG')

    else:
        app.config.from_object('cyber_role.config.development')

    #Config elasticsearch
    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
        if app.config['ELASTICSEARCH_URL'] else None



    # Custom jinja helpers
    app.jinja_env.globals['url_for_self'] = url_for_self
    app.jinja_env.globals.update(create_hashid=hashids_hasher.encode)
    app.jinja_env.filters['datetime'] = format_datetime


    # Whitespacing Jinja
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    # Setup Hashids
    hashids_hasher.init_hasher(app)

    # Setup localization
    babel.init_app(app)

    # Setup CSRF protection
    csrf.init_app(app)

    # Setup database
    db.init_app(app)


    # Setup mail
    mail.init_app(app)

    # # Setup Celery
    # celery=make_celery(app)

    # #configure/initialize all your extensions
    # # db.init_app(app)
    # # celery.init_app(app)

    # app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
    # app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

    # Force model registration
    from cyber_role import models

    # Database migrations
    migrations_dir = os.path.join(app.root_path, 'migrations')
    migrate.init_app(app, db, migrations_dir)

    # Setup Flask-User
    user_db_adapter = SQLAlchemyAdapter(db, models.User)
    user_manager.init_app(app, db_adapter=user_db_adapter)


    # Setup Flask-Login
    # login_manager.init_app(app)
    # login_manager.login_view = 'user_ksat.login'
    # login_manager.login_message = _('Please login to continue')
    # login_manager.login_message_category = 'info'
    # # login_manager.refresh_view = 'auth.reauthenticate'
    # # login_manager.needs_refresh_message = (
    # #     _('To protect your account, please reauthenticate to access this page.')
    # # )
    # # login_manager.needs_refresh_message_category = 'info'

    # Setup Flask-Misaka
    md.init_app(app)


    # if app.config.get('USE_CELERY', False):
    #     celery.init_app(app)
    # Setup Flask-Assets and bundles
    """
    assets.init_app(app)
    libsass = webassets.filter.get_filter(
        'libsass',
        style='compressed'
    )

    scss_bundle = Bundle(
        'app.scss',
        depends='scss/custom.scss',
        filters=libsass
    )

    css_bundle = Bundle(
        scss_bundle,
        filters='cssmin',
        output='gen/packed.css'
    )

    js_bundle = Bundle(
        'js/vendor/zepto.min.js',
        'js/vendor/noty.min.js',
        'js/vendor/bulma-tagsinput.min.js',
        'js/navigation.js',
        'js/init.js',
        filters='rjsmin',
        output='gen/packed.js'
    )

    assets.register('css_pack', css_bundle)
    assets.register('js_pack', js_bundle)
    """


    # Register blueprints
    from cyber_role.views.general import bp_general
    from cyber_role.views.user_ksat import bp_user_ksat
    from cyber_role.views.lo import bp_lo
    from cyber_role.views.manage import bp_manage

    app.register_blueprint(bp_general)
    app.register_blueprint(bp_user_ksat)
    app.register_blueprint(bp_lo)
    app.register_blueprint(bp_manage)

    # Custom commands
    from cyber_role import commands

    # Custom error handlers
    app.register_error_handler(403, forbidden)
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, server_error)

    return app


