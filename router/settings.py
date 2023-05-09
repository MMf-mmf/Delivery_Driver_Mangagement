# THIS FILE IS NOT IN USE RATHER THE SETTINGS IN THE SETTINGS FOLDER ARE USED INSTEAD
import os
from pathlib import Path
from environs import Env
from django.contrib.messages import constants as messages
from google.oauth2 import service_account



env = Env()
env.read_env()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/


SECRET_KEY = env("DJANGO_SECRET_KEY")

# DEBUG = env.bool("DJANGO_DEBUG", default=False)

ALLOWED_HOSTS = ['routerapp.onrender.com'] # , '127.0.0.1', '10.0.0.56'


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites', # for all auth
    # APPS
    'accounts_app.apps.AccountsAppConfig',
    'scheduler_app.apps.SchedulerAppConfig',
    # PIP INSTALLS
    'rest_framework',
    "crispy_forms",
    "crispy_bootstrap5",
    'django_htmx',
    "whitenoise.runserver_nostatic",
    'allauth',
    'allauth.account', 
    "django_extensions",
    'debug_toolbar',
    'django_twilio',
    'django_cleanup.apps.CleanupConfig', # this app should always be last
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'router.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
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

WSGI_APPLICATION = 'router.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

# for development
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': env("DATABASE_NAME"),
#         'USER': env("DATABASE_USER"),
#         'PASSWORD': env("DATABASE_PASSWORD"),
#         'CONN_MAX_AGE': None, # for production
#     }
# }

# for production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env("DATABASE_NAME"),
        'USER': env("DATABASE_USER"),
        'PASSWORD': env("DATABASE_PASSWORD"),
        'HOST': env("DATABASE_HOST"), # for production
        'PORT': env("DATABASE_PORT"), # for production
        'CONN_MAX_AGE': None, # for production
    }
}


'''docker set up'''
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": "postgres",
#         "USER": "postgres",
#         "PASSWORD": "postgres",
#         "HOST": "db",  # set in docker-compose.yml
#         "PORT": 5432,  # default postgres port
#     }
# }
# django_project/settings.py
AUTH_USER_MODEL = "accounts_app.CustomUser" 


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators
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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'EST'

USE_I18N = True

USE_TZ = True

GOOGLE_API_KEY = env("GOOGLE_API_KEY")

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'),]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]
# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

# Base url to serve media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

#################  Google Cloud storage  ##############
GS_BUCKET_NAME = "router_media" 
DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
#MEDIA_URL = "https://console.cloud.google.com/storage/browser/router_media"
GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
    "googleauth.json"
)





DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"


CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
MESSAGE_TAGS = {
        messages.DEBUG: 'alert-secondary',
        messages.INFO: 'alert-info',
        messages.SUCCESS: 'alert-success',
        messages.WARNING: 'alert-warning',
        messages.ERROR: 'alert-danger',
 }


"""allauth config"""
LOGIN_REDIRECT_URL = 'home'
ACCOUNT_LOGOUT_REDIRECT = 'home' 
SITE_ID = 1
AUTHENTICATION_BACKENDS = (
'django.contrib.auth.backends.ModelBackend',
'allauth.account.auth_backends.AuthenticationBackend',
)
ACCOUNT_SESSION_REMEMBER = True
# ACCOUNT_LOGOUT_ON_GET = True
# config to have email login
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True 
ACCOUNT_UNIQUE_EMAIL = True 


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# TEXT SETTINGS
TWILIO_ACCOUNT_SID = env('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = env('TWILIO_AUTH_TOKEN')
# TWILIO_DEFAULT_CALLERID = env('TWILIO_DEFAULT_CALLERID')
TWILIO_PHONE_NUMBER = env('TWILIO_DEFAULT_CALLERID')

DEV_PHONE_NUMBER = env('DEV_PHONE_NUMBER')

import socket
hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
# INTERNAL_IPS = [ip[:-1] + "1" for ip in ips]  # when running in docker
INTERNAL_IPS = ['127.0.0.1','10.0.0.56'] 


# HTTPS SETTINGS
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
SECURE_HSTS_SECONDS = env.int("DJANGO_SECURE_HSTS_SECONDS", default=2592000)  # 30 days
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True)
SECURE_HSTS_PRELOAD = env.bool("DJANGO_SECURE_HSTS_PRELOAD", default=True)
SESSION_COOKIE_SECURE = env.bool("DJANGO_SESSION_COOKIE_SECURE", default=True)
CSRF_COOKIE_SECURE = env.bool("DJANGO_CSRF_COOKIE_SECURE", default=True)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")