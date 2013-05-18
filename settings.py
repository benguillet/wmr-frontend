# Django settings for WebMapReduce project.


# Detect project path and setup sys.path

import sys
from os import path
PROJECT_PATH = path.normpath(path.dirname(path.abspath(__file__)))

lib_path = path.join(PROJECT_PATH, 'lib')
sys.path.append(lib_path)


DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': path.join(PROJECT_PATH, 'db', 'database.sqlite'),  # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = path.join(PROJECT_PATH, 'media')

# Make this unique, and don't share it with anybody.
SECRET_KEY = '9kvvyam(xb2gf+bf^=o&_%vwsm_o6+o-6o^bs+-50-c46f9n@2'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    path.join(PROJECT_PATH, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.webdesign',
    'wmr',
    'registration',
    'south',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.contrib.messages.context_processors.messages",
    'registration.context_processors.registration_enabled',
)

# Auth-related settings

REGISTRATION_ENABLED=True
REQUIRE_REGISTRATION_KEY=True

SESSION_EXPIRE_AT_BROWSER_CLOSE=True



# Apply overrides in settings_local.py
try:
    from settings_local import *
except ImportError:
    pass


# Get a prefix to use for the following URLs if appropriate
_settings = globals()
_script_prefix = _settings.get('FORCE_SCRIPT_NAME', '')

# Set media URLs
if 'MEDIA_URL' not in _settings:
    MEDIA_URL = _script_prefix + '/media/'
if 'ADMIN_MEDIA_PREFIX' not in _settings:
    ADMIN_MEDIA_PREFIX = MEDIA_URL + 'admin/'

# Set login/logout URLs
if 'LOGIN_REDIRECT_URL' not in _settings:
    LOGIN_REDIRECT_URL = _script_prefix + '/'
if 'LOGIN_URL' not in _settings:
    LOGIN_URL = _script_prefix + '/accounts/login/'
if 'LOGOUT_URL' not in _settings:
    LOGOUT_URL = _script_prefix + '/accounts/logout/'
