import base

DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'takeone',
        'USER': 'byy',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '',
    }
}


# static and media

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATICFILES_DIRS = [
    os.path.join(FILE_DIR, "static"),
]

STATIC_ROOT = 'staticfiles'

MEDIA_ROOT = 'mediafiles'