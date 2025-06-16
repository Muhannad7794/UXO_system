from pathlib import Path
import os
import sys

# import dotenv
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()  # This will load from '.env' by default if it exists.
# For the GIS setup, docker-compose's env_file directive handles .env.gis.

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")


DEBUG_STR = os.getenv("DJANGO_DEBUG", "False")
DEBUG = DEBUG_STR.lower() in ("true", "1", "t")


ALLOWED_HOSTS_STR = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STR.split(",") if host.strip()]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",  # ADDED: GeoDjango application
    # 3rd Party Apps
    "rest_framework",
    "rest_framework_gis",  # ADDED: DRF GIS for GeoJSON support
    "django_filters",  # ADDED: For filtering support in DRF
    "drf_spectacular",
    "django_htmx",  # ADDED: HTMX support for Django
    # local apps
    "uxo_records",
    "danger_score",
    "citizens_reports",
    "reports",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "uxo_backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
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

WSGI_APPLICATION = "uxo_backend.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        # UPDATED: Engine to use PostGIS
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "HOST": os.getenv("DB_HOST"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "PORT": os.getenv("DB_PORT"),
        "NAME": os.getenv("DB_NAME"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Frontend and URL configuration
## Static files (CSS, JavaScript, Images)
## https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
# STATIC_ROOT = BASE_DIR / "staticfiles"

## Login redirect URL
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    # Added default pagination for consistency
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    # Default filters path
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}

SPECTACULAR_SETTINGS = {
    "TITLE": "UXO Prioritization API",
    "DESCRIPTION": (
        "API backend for the UXO Prioritization and Risk Assessment System.\n\n"
        "This API allows users to:\n"
        "- View UXO records across regions\n"
        "- View regional GIS data with danger scores\n"
        "- Filter/search by region, ordnance type, and condition\n"
        "- Generate visualized data-based reports built on different ML and statistical models\n"
        "- Create and manage UXO entries (authenticated users only)\n"
        "\nSecurity Note:\n"
        "Write operations (POST, PATCH, DELETE) require authentication."
    ),
    "VERSION": "1.0.0",
    "SCHEMA_PATH_PREFIX": "/api/v1",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SERIALIZER_EXTENSIONS": {
        "rest_framework_gis.fields.GeometryField": "drf_spectacular.extensions.OpenApiSerializerFieldExtension",
    },
    # DEFAULT_PAGINATION_CLASS and PAGE_SIZE
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "defaultModelRendering": "example",
        "defaultModelsExpandDepth": -1,
        "docExpansion": "none",  # list, full, or none
        "filter": True,
        "persistAuthorization": True,
    },
}
