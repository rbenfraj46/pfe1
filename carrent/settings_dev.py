from carrent.settings import *

DEBUG = True


if DEBUG:
    INSTALLED_APPS += [
        'debug_toolbar',
        'django_extensions',
        ]
    MIDDLEWARE += [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
        ]

    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': 'carrental',
            'USER': 'myuser',
            'PASSWORD': '12345',
            'HOST': 'localhost',  
            'PORT': '5432',
        }
    } 

    INTERNAL_IPS = [
        '127.0.0.1',
        ]

    DEBUG_TOOLBAR_PANELS =  [
        'debug_toolbar.panels.history.HistoryPanel',
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
        'debug_toolbar.panels.profiling.ProfilingPanel',
    ]
    # DATABASES = {
    #     'default': {
    #         'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #         'NAME': 'tracking',
    #         'USER': 'tracking',
    #         'PASSWORD': 'tracking',
    #         'HOST': '127.0.0.1',
    #         'PORT': '5432',
    #     }
    # }
    TEMPLATE_DEBUG = DEBUG
    ALLOWED_HOSTS += ['*']
    RAVEN_CONFIG = { 'dsn': ''}
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

    EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
    EMAIL_FILE_PATH = str(BASE_DIR.joinpath('sent_emails'))
