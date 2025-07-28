import os
import dj_database_url
from .settings import *
from .settings import BASE_DIR

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')

ALLOWED_HOSTS = []
CSRF_TRUSTED_ORIGINS = []

if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
    CSRF_TRUSTED_ORIGINS.append('https://' + RENDER_EXTERNAL_HOSTNAME)
else:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']
    CSRF_TRUSTED_ORIGINS = ['http://localhost:8000']


DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-CHANGE-THIS-DEV-KEY')

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS_ALLOWED_ORIGINS = [
#     "https://swapskill-99mj.onrender.com",
#     "http://localhost:5173",
# ]

STORAGES = {
    'default': {
        'BACKEND': "django.core.files.storage.FileSystemStorage",  
    },
    'staticfiles': {
        "BACKEND" : "whitenoise.storage.CompressedStaticFilesStorage",
    }
}


DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite3'),
        conn_max_age=600,
    )
}

