"""
Django settings for diseraca project.

Generated by 'django-admin startproject' using Django 1.8.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_HOST_USER = 'noreplypropalma@gmail.com'
#EMAIL_HOST_PASSWORD = 'propalma2015'
#EMAIL_HOST_USER = 'no.reply.diseraca@gmail.com'

#EMAIL_HOST_PASSWORD = 'diseraca32300'

#EMAIL_PORT = 587
EMAIL_HOST = 'mail.ufps.edu.co'
EMAIL_HOST_USER = 'diseraca'
EMAIL_HOST_PASSWORD = 'Diseraca2016+'
EMAIL_PORT = 465
EMAIL_USE_SSL = True

# TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'x&i*8z2e*=mr#+45dd3*$k03y!sn=!e6j046g07s8@&k6pghk9'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    # 'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'laboratorios',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'diseraca.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'diseraca.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'silabsa',
        'USER': 'postgres',
        'PASSWORD': 'diseraca',
        'HOST': '192.168.9.5',
        'PORT': '5432',
    }
}

'''
'NAME': 'diseraca_lab',
        'USER': 'diseraca_lab',
        'PASSWORD': 'Camisa!0##',
        'HOST': 'localhost',

'NAME': 'silabsa',
        'USER': 'root',
        'PASSWORD': 'Alto"##0',
        'HOST': '192.168.9.6',

'NAME': 'silabsa_developed',
        'USER': 'admin',
        'PASSWORD': 'Alto"##0',
        'HOST': '192.168.9.6',

'''



# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'es'


TIME_ZONE = 'America/Bogota'
# 'UTC'
DATETIME_INPUT_FORMATS = (
    '%Y-%m-%d %H:%M:%S',
)
USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, "static")

#STATICFILES_DIRS = (
#    os.path.join(BASE_DIR, "static_pro", "our_static"),
#)