"""
Django settings for takeone project.

Generated by 'django-admin startproject' using Django 1.9.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_DIR = os.path.dirname(os.path.abspath(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',

    'crispy_forms',
    'storages',
    'boto',
    'registration',
    'django_twilio',
    'stripe',

    'newsletter',
    'photographer',
    'reserve',
    'sms',
    'blog',
    'userprofile',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'takeone.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'takeone.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
    }
}


# cache engine
def get_cache():
  import os
  try:
    os.environ['MEMCACHE_SERVERS'] = os.environ['MEMCACHIER_SERVERS'].replace(',', ';')
    os.environ['MEMCACHE_USERNAME'] = os.environ['MEMCACHIER_USERNAME']
    os.environ['MEMCACHE_PASSWORD'] = os.environ['MEMCACHIER_PASSWORD']
    return {
      'default': {
        'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
        'TIMEOUT': 500,
        'BINARY': True,
        'OPTIONS': { 'tcp_nodelay': True }
      }
    }
  except:
    return {
      'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
      }
    }

CACHES = get_cache()



# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/


# registration redux
ACCOUNT_ACTIVATION_DAYS = 7
REGISTRATION_AUTO_LOGIN = True
LOGIN_REDIRECT_URL = '/profile'
SITE_ID = 1
SITE_URL = 'http://brytephoto.com'
SITE_EMAIL = 'hello@brytephoto.com'


# email 
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True


# crispy form
CRISPY_TEMPLATE_PACK = 'bootstrap3'


# Parse database configuration from $DATABASE_URL
import dj_database_url
DATABASES['default'] = dj_database_url.config()

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['www.brytephoto.com', 'brytephoto.com']

# Static asset configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

MEDIA_ROOT = 'mediafiles'
MEDIA_URL = '/media/'

STATICFILES_DIRS = [
    os.path.join(FILE_DIR, "static"),
]

STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'


# try:
#     from .local_settings import *
# except ImportError:
#     pass


# security
# SESSION_COOKIE_SECURE = True
# SECURE_BROWSER_XSS_FILTER = True
# SECURE_CONTENT_TYPE_NOSNIFF = True
# CSRF_COOKIE_SECURE = True
# CSRF_COOKIE_HTTPONLY = True


# Amazon S3
# if not DEBUG:

MEDIA_ROOT = '/media/'
STATIC_ROOT = '/static/'

STATICFILES_STORAGE = 'custom_storages.StaticStorage'
DEFAULT_FILE_STORAGE = 'custom_storages.MediaStorage'

AWS_STORAGE_BUCKET_NAME = "take-one"
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_PRELOAD_METADATA = True
S3_URL = 'http://%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME


STATIC_URL = S3_URL + STATIC_ROOT
MEDIA_URL = S3_URL + MEDIA_ROOT



# twilio
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
# temp setting for testing
DJANGO_TWILIO_FORGERY_PROTECTION = False

BEN_CELL = os.environ.get('BEN_CELL')
TWILIO_CELL = os.environ.get('TWILIO_CELL')

STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
CLIENT_ID = 'ca_7ogFyyC52p69QQf6ysSG5jpAcXmEFovq'
COMMISSION = os.environ.get('COMMISSION')

# mixpanel
MIXPANEL_TOKEN = 'b27c2c4d1dddc024a8c4b60b153f2968'

# dropbox
DROPBOX_TOKEN = os.environ.get('DROPBOX_TOKEN')