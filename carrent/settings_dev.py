from carrent.settings import *

DEBUG = True

ALLOWED_HOSTS = [
    '127.0.0.1', 
    'localhost', 
    'scaling-bassoon-7vrgj675g96wcwp97-8000.app.github.dev'
]

CSRF_TRUSTED_ORIGINS = [
    "https://scaling-bassoon-7vrgj675g96wcwp97-8000.app.github.dev",
    "http://127.0.0.1:8000",
    "http://localhost:8000"
]

# Application definition
if DEBUG:
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
        'debug_toolbar',
        'django_extensions',
    ]
    
    MIDDLEWARE += [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]

    # Configuration de la base de données
    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': 'carrental',
            'USER': 'myuser',
            'PASSWORD': '12345',
            'HOST': 'postgresql',  
            'PORT': '5432',
        }
    } 

    INTERNAL_IPS = ['127.0.0.1']

    # Configuration de Django Debug Toolbar
    DEBUG_TOOLBAR_PANELS = [
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

    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: True,
        'RESULTS_CACHE_SIZE': 100,
        'SQL_WARNING_THRESHOLD': 100,
    }

    # Configuration de Django Extensions
    SHELL_PLUS = "ipython"
    SHELL_PLUS_PRINT_SQL = True
    NOTEBOOK_ARGUMENTS = [
        '--ip', '0.0.0.0',
        '--port', '8888',
        '--allow-root',
        '--no-browser',
    ]

    # Configuration de Jazzmin pour le développement
    JAZZMIN_SETTINGS = {
        # Interface utilisateur
        "site_title": "TunCar Admin (DEV)",
        "site_header": "TunCar (Développement)",
        "site_brand": "TunCar Dev",
        "site_logo": "images/logo.png",
        "welcome_sign": "Bienvenue dans l'environnement de développement",
        "copyright": "TunCar - Environnement de développement",
        
        # Thème et couleurs
        "theme": "flatly",
        "dark_mode_theme": "darkly",
        
        # Navigation
        "show_sidebar": True,
        "navigation_expanded": True,
        "hide_apps": [],
        "hide_models": [],
        
        # Interface utilisateur
        "changeform_format": "horizontal_tabs",
        "related_modal_active": True,
        "custom_css": "admin/css/custom_admin.css",
        "custom_js": "admin/js/custom_admin.js",
        
        # Recherche
        "search_model": ["auth.User", "cars.CarModel", "cars.Brand", "home.Agences"],
        
        # Menu latéral
        "order_with_respect_to": ["auth", "cars", "home"],
        
        # Icônes (Font Awesome)
        "icons": {
            "auth": "fas fa-users-cog",
            "auth.user": "fas fa-user",
            "auth.Group": "fas fa-users",
            "cars.CarModel": "fas fa-car",
            "cars.Brand": "fas fa-copyright",
            "cars.GearType": "fas fa-cog",
            "cars.Transmission": "fas fa-exchange-alt",
            "cars.AgencyCar": "fas fa-warehouse",
            "cars.CarReservation": "fas fa-calendar-check",
            "cars.CarUnavailability": "fas fa-calendar-times",
            "cars.CarModelRequest": "fas fa-question-circle",
            "home.User": "fas fa-user-circle",
            "home.Agences": "fas fa-building",
            "home.Contact": "fas fa-envelope",
            "home.Devise": "fas fa-money-bill",
            "home.State": "fas fa-map-marker",
            "home.City": "fas fa-city",
            "home.Delegation": "fas fa-map",
        },
        
        # Liens personnalisés dans le menu
        "custom_links": {
            "cars": [{
                "name": "Statistiques (DEV)", 
                "url": "admin:car_stats",
                "icon": "fas fa-chart-line"
            }],
            "home": [{
                "name": "Documentation API", 
                "url": "/api/docs/",
                "icon": "fas fa-book"
            }]
        },
        
        # Options supplémentaires pour le développement
        "show_ui_builder": True,
        "changeform_format_overrides": {
            "auth.user": "collapsible",
            "auth.group": "horizontal_tabs",
        },
        "related_modal_active": True,
    }

    # Personnalisation de l'interface utilisateur Jazzmin
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
        "dark_mode_theme": "darkly",
        "button_classes": {
            "primary": "btn-primary",
            "secondary": "btn-secondary",
            "info": "btn-outline-info",
            "warning": "btn-outline-warning",
            "danger": "btn-outline-danger",
            "success": "btn-outline-success"
        }
    }

    TEMPLATE_DEBUG = DEBUG
    ALLOWED_HOSTS += ['*']
    RAVEN_CONFIG = { 'dsn': ''}
    
    # Sécurité désactivée en développement
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

    # Configuration des emails en développement
    EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
    EMAIL_FILE_PATH = str(BASE_DIR.joinpath('sent_emails'))
    
    # Configuration des médias
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

    # Cache pour le développement
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }

    # Configuration de logging détaillée
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
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
                'formatter': 'verbose',
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': os.path.join(BASE_DIR, 'debug.log'),
                'formatter': 'verbose',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': True,
            },
            'cars': {
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'home': {
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
                'propagate': True,
            },
        },
    }



