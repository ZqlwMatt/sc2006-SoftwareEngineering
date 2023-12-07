import os
from pathlib import Path
import pymysql as pymysql

from configparser import RawConfigParser

BASE_DIR = Path(__file__).resolve().parent.parent
APP_NAME = "iHateCongestion"


def get_variable(section_name, variable_name, config=None):
    if not config:  # run from GitHub Action
        return os.environ.get(variable_name.upper())
    else:
        return config.get(section_name, variable_name)


config = None

if os.path.exists(BASE_DIR.parent / "secrets/config.ini"):
    config = RawConfigParser()
    config.read(BASE_DIR.parent / "secrets/config.ini")
elif os.path.exists(BASE_DIR / "config.ini"):
    config = RawConfigParser()
    config.read(BASE_DIR / "config.ini")

# TODO: Deployment checklist

SECRET_KEY = get_variable("app", "secret_key", config=config)
environment = get_variable("env", "environment", config=config)
googlemaps_api_key = get_variable("app", "googlemaps_api_key", config=config)

if environment == "production" or environment == "production_github":
    SESSION_ENVIRONMENT_PRODUCTION = True
elif environment == "development":
    SESSION_ENVIRONMENT_PRODUCTION = False
else:
    raise ValueError(
        "Check the config.ini file and make sure the environment "
        "variable is set to either 'production' or 'development'"
    )

DEBUG = True
if SESSION_ENVIRONMENT_PRODUCTION:
    DEBUG = False

ALLOWED_HOSTS = ["127.0.0.1", "172.21.148.165"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "main",
    "crispy_forms",
    "crispy_bootstrap5",
    "django_select2",
    "django_tables2",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "sc2006_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
                    BASE_DIR / "templates",
                ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "sc2006_project.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DB_USER = get_variable("app", "db_user", config=config)
DB_PASS = get_variable("app", "db_pass", config=config)

USE_MYSQL = True

if not USE_MYSQL:
    db_defaults = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
else:
    db_defaults = {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "app_db2",
        "USER": DB_USER,
        "PASSWORD": DB_PASS,
        "HOST": "127.0.0.1",
        "PORT": 3306,
        "OPTIONS": {
            "charset": "utf8mb4",
        },
        "TEST": {
            "NAME": "test_app_db",
        }
    }
    pymysql.version_info = (1, 4, 3, "final", 0)
    pymysql.install_as_MySQLdb()

if SESSION_ENVIRONMENT_PRODUCTION:
    db_defaults["CONN_MAX_AGE"] = 90

DATABASES = {
    "default": db_defaults,
}

if environment == "production":
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://localhost:6379/1",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
        },
        "select2": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://localhost:6379/2",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
        },
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        },
        "select2": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        },
    }

SELECT2_CACHE_BACKEND = "select2"

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Singapore"

USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / STATIC_URL]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "/login/"
LOGOUT_REDIRECT_URL = "/"

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
