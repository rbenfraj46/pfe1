"""
tests settings
"""
from carrent.settings import *


TEMPLATE_DEBUG = DEBUG = False

for item in ('debug_toolbar', 'django_extensions'):
    if item in INSTALLED_APPS:
        INSTALLED_APPS.remove(item)
if 'debug_toolbar.middleware.DebugToolbarMiddleware' in MIDDLEWARE:
    MIDDLEWARE.remove('debug_toolbar.middleware.DebugToolbarMiddleware')

HTML_MINIFY = False

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.spatialite',
        'NAME': BASE_DIR / 'db.sqlite3.tests',
    }
}
