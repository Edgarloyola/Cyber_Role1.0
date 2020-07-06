"""Development configuration."""
import os

SECRET_KEY = "potato"
# DEBUG = True
# TESTING = True


# Database path
SQLALCHEMY_DATABASE_URI = "postgresql://localhost/cyber_role?user=admin&password=admin1234"


# Elasticsearch
ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')


# Celery
USE_CELERY = True
CELERY_BROKER_URL = 'redis://localhost:6379/1'
CELERY_RESULT_BACKEND = 'postgresql://localhost/cyber_role?user=admin&password=admin1234'

# Site name
SITENAME = 'cyber_role'

# Items per page in pagination
PAGE_ITEMS = 20

# Hashids
HASHIDS_SALT = 'hashedpotatoes'
HASHIDS_LENGTH = 8

# Flask-User
USER_APP_NAME = SITENAME

# Flask-Mail
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 465
# MAIL_USE_TLS = True
MAIL_USE_SSL = True
# MAIL_DEFAULT_SENDER = ""
MAIL_DEBUG = True
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = 'edgaryour25@gmail.com'
