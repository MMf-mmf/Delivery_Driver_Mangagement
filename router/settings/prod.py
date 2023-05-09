from .base import *


DEBUG = False
ALLOWED_HOSTS = [''] 



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env("DATABASE_NAME"),
        'USER': env("DATABASE_USER"),
        'PASSWORD': env("DATABASE_PASSWORD"),
        'HOST': env("DATABASE_HOST"),
        'PORT': env("DATABASE_PORT"), 
        'CONN_MAX_AGE': None, 
    }
}


ADMINS = [
'',
]