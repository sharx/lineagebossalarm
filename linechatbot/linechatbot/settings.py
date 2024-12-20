"""
Django settings for linechatbot project.

Generated by 'django-admin startproject' using Django 5.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
# Import dj-database-url at the beginning of the file.
import dj_database_url
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-+9)5=#5k7&7hry0_ow1^d+_qf8pt46_wnl-o31)dfvk=bd@xfq'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #add for custom app
    'webhook',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #add this for renderer.com to serve static files
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'linechatbot.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                #add this for postgres
                'whitenoise.middleware.WhiteNoiseMiddleware',
            ],
        },
    },
]

WSGI_APPLICATION = 'linechatbot.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    #'default': {
    #    'ENGINE': 'django.db.backends.sqlite3',
    #    'NAME': BASE_DIR / 'db.sqlite3',
    #}
    #use this for renderer internal postgres url
    'default': dj_database_url.config(
        # Replace this value with your local database's connection string.
        default='postgresql://lineage:z2rYptjMQhiBIuVU5OhDExxtmtHuhyHa@dpg-cscjaiaj1k6c7396q8g0-a/lineagedb',
        conn_max_age=600
    )
    #use this for external postgres url from render.com
    #'default': {
    #    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #    'NAME': 'lineagedb',
    #    'USER': 'lineage',
    #    'PASSWORD': 'z2rYptjMQhiBIuVU5OhDExxtmtHuhyHa',
    #    'HOST': 'dpg-cscjaiaj1k6c7396q8g0-a.oregon-postgres.render.com',
    #    'PORT': '5432',
    #}
    #use this for intermal postgres url from render.com
    #'default': {
    #    'ENGINE': 'django.db.backends.postgresql',
    #    'NAME': 'lineagedb',
    #    'USER': 'lineage',
    #    'PASSWORD': 'z2rYptjMQhiBIuVU5OhDExxtmtHuhyHa',
    #    'HOST': 'postgresql://lineage:z2rYptjMQhiBIuVU5OhDExxtmtHuhyHa@dpg-cscjaiaj1k6c7396q8g0-a/lineagedb',
    #    'PORT': '5432',
    #}
}



# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

# This setting informs Django of the URI path from which your static files will be served to users
# Here, they well be accessible at your-domain.onrender.com/static/... or yourcustomdomain.com/static/...
STATIC_URL = '/static/'

# This production code might break development mode, so we check whether we're in DEBUG mode
#if not DEBUG:
# Tell Django to copy static assets into a path called `staticfiles` (this is specific to Render)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Enable the WhiteNoise storage backend, which compresses static files to reduce disk use
# and renames the files with unique names for each version to support long-term caching
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
