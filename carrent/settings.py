#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Django settings for rent_car project.

Generated by 'django-admin startproject' using Django 3.2.10.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from pathlib import Path

from django.utils.translation import gettext_lazy as _


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-f5x0_-p)6$+jp2aw=(f2(r9f0*def@$n5lpx8@*1a$)z2nfd^#'



ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'jazzmin',  # Doit être avant django.contrib.admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'djgeojson',
    'leaflet',
    'captcha',
    'axes',
    'home',
    'cars',
    #'carrent',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
    'htmlmin.middleware.HtmlMinifyMiddleware',
    'htmlmin.middleware.MarkRequestMiddleware',
]


AUTHENTICATION_BACKENDS = [
    # AxesBackend should be the first backend in the AUTHENTICATION_BACKENDS list.
    'axes.backends.AxesBackend',

    # Django ModelBackend is the default authentication backend.
    'carrent.authentication.EmailAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
]


ROOT_URLCONF = 'carrent.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates/'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],

            'libraries': {
                'html_tag': 'home.templatetags.tags',
            },
        },
    },
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {filename} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            #'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
        'formatter': 'verbose',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },

}

WSGI_APPLICATION = 'carrent.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.spatialite',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

USE_GIS = False

if USE_GIS:
    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': 'gis',
            'USER': 'user001',
            'PASSWORD': '123456789',
            'HOST': 'localhost',
            'PORT': '15432'
        }
    }


# LEAFLET_CONFIG = {
#     'SPATIAL_EXTENT': (5.0, 44.0, 7.5, 46)
# }

DEFAULT_LON = '10.3124463'
DEFAULT_LAT = '36.8325412'

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en'
LANGUAGES = [
    ('en', _('English')),
    ('fr', _('French')),
    ('ar', _('Arabic')),
]
LOCALE_PATHS = [
    BASE_DIR / 'locale/',
]


#TIME_ZONE = 'Africa/Tunis'
TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

NO_REPLY_EMAIL_ADRESS = 'noreply@tuncar.tn'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static/'), ]


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# axes config: https://django-axes.readthedocs.io/en/latest/4_configuration.html
AXES_FAILURE_LIMIT = 3
AXES_RESET_ON_SUCCESS = True

# Axes reverse proxy configuration

CAPTCHA_IMAGE_SIZE = (180, 35)
CAPTCHA_FONT_SIZE = 30
CAPTCHA_LENGTH = 6
CAPTCHA_SOX_PATH = '/usr/bin/sox'
CAPTCHA_FLITE_PATH = '/usr/bin/flite'

#LOGIN LOGOUT URL
LOGOUT_REDIRECT_URL = "/"
LOGIN_REDIRECT_URL = "/"
LOGIN_URL = 'login'  # Modifié pour utiliser le nom d'URL au lieu du chemin
LOGOUT_URL = 'logout.php'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

AUTH_USER_MODEL = 'home.User'

# confirm that the given mail is valid
SEND_CONFIRMATION_MAIL = True

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = "noreply.tuncar@gmail.com"
EMAIL_HOST_PASSWORD = "SjBDn3uq4vTP2m9"

HTTP_PROXY = ""
DEFAULT_CURRENCY = 'TND'
FREECURRENCYAPI_TOKEN = "d494c180-8092-11ec-bdc1-992577c28051"

#AUtomobile.tn scrapy
AUTOMOBILE_TN_URL  = "https://www.automobile.tn/fr/neuf"
AUTOMOBILE_TN_BASE_URL = "https://www.automobile.tn"
AUTOMOBILE_TN_DOWNLOAD_IMAGES = True
CAR_DOWNLOAD_FOLDER = "/cars/brands/"

#HTML_MINIFY = True

SPATIALITE_LIBRARY_PATH = '/usr/lib/x86_64-linux-gnu/mod_spatialite.so'

GEOIP_KEY = "A2h5fPXmqQNYZCqz"

# Admin site customization
JAZZMIN_SETTINGS = {
    "site_title": "TunCar Admin",
    "site_header": "TunCar",
    "site_brand": "TunCar",
    "welcome_sign": "Bienvenue dans l'administration TunCar",
    "copyright": "TunCar",
    "show_ui_builder": True,
    "changeform_format": "horizontal_tabs",
    "related_modal_active": True,
    "custom_css": "admin/css/custom_admin.css",
    "custom_js": "admin/js/custom_admin.js",
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "cars.CarModel": "fas fa-car",
        "cars.Brand": "fas fa-copyright",
        "cars.AgencyCar": "fas fa-warehouse",
        "cars.CarReservation": "fas fa-calendar-check",
        "home.Agences": "fas fa-building",
        "home.Contact": "fas fa-envelope",
    },
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-circle",
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": ["auth", "cars", "home"],
    "custom_links": {
        "cars": [{
            "name": "Statistiques des réservations", 
            "url": "admin:car_stats",
            "icon": "fas fa-chart-line",
        }]
    },
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}
