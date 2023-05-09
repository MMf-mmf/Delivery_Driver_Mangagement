from .base import *
import socket

DEBUG = True
ALLOWED_HOSTS = ['routerapp.onrender.com', '127.0.0.1', '10.0.0.56'] 


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env("DATABASE_NAME"),
        'USER': env("DATABASE_USER"),
        'PASSWORD': env("DATABASE_PASSWORD"),
    }
}

hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
# INTERNAL_IPS = [ip[:-1] + "1" for ip in ips]  # when running in docker
INTERNAL_IPS = ['127.0.0.1','10.0.0.56'] 