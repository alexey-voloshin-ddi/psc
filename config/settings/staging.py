"""
Local settings

- Run in Debug mode

- Use console backend for emails

- Add Django Debug Toolbar
- Add django-extensions as app
"""

from .base import *  # noqa

# DEBUG
# ------------------------------------------------------------------------------
DEBUG = env.bool('DJANGO_DEBUG', default=True)
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key only used for development and testing.
SECRET_KEY = env('DJANGO_SECRET_KEY', default='li-*>XuQF61_p:ER#q((WQ-+#pZ>|+z@k>(>OMTN|p]K4qy}%_')

# Mail settings
# ------------------------------------------------------------------------------

# EMAIL_PORT = 1025
#
# EMAIL_HOST = 'localhost'
# EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND',
#                     default='django.core.mail.backends.console.EmailBackend')


# CACHING
# ------------------------------------------------------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': ''
    }
}

# django-debug-toolbar
# ------------------------------------------------------------------------------
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware', ]
INSTALLED_APPS += ['debug_toolbar', ]

INTERNAL_IPS = ['127.0.0.1', '10.0.2.2', ]

DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': [
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ],
    'SHOW_TEMPLATE_CONTEXT': True,
}

# django-extensions
# ------------------------------------------------------------------------------
INSTALLED_APPS += ['django_extensions', ]

# TESTING
# ------------------------------------------------------------------------------
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

########## CELERY
# In development, all tasks will be executed locally by blocking until the task returns
CELERY_ALWAYS_EAGER = False
########## END CELERY

# Your local stuff: Below this line define 3rd party library settings
# ------------------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DATABASE_NAME'),
        'PASSWORD': env('DATABASE_PASSWORD'),
        'USER': env('DATABASE_USER'),
        'HOST': env('DATABASE_HOST'),
        'PORT': env('DATABASE_PORT'),
    },
    'duplicate': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': "psc_duplicate",
        'PASSWORD': env('DATABASE_PASSWORD'),
        'USER': env('DATABASE_USER'),
        'HOST': env('DATABASE_DUPLICATE_HOST'),
        'PORT': env('DATABASE_PORT'),
    },
}


STATICFILES_DIRS = (
   str(APPS_DIR.path('static')),
)

ALLOWED_HOSTS = ['*']

CELERY_BROKER_URL = env("CELERY_BROKER_URL")

EMAIL_USE_TLS = True
# EMAIL_HOST = 'smtp.mailgun.org'
# EMAIL_HOST_USER = 'postmaster@anvileight.com'
# EMAIL_HOST_PASSWORD = 'f377e1b19f562236b398eefc0cd55bee'
# EMAIL_PORT = 587

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = 'Artem.Sklar'
EMAIL_HOST_PASSWORD = '&#v@:EB\Tn5/&&Jk'
EMAIL_PORT = 587

MEDIA_ROOT = '/srv/media'

SUMMARY_EMAIL_TO = ['cbortos@multimindmedia.com', 'istormi@mail.ru', 'artem.sklar@anvileight.com']
# SUMMARY_EMAIL_TO = ['admin@example.com', ]
