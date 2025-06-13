from pathlib import Path
import os
import sys

# import dotenv
from dotenv import load_dotenv

# Load environment variables from .env file
# When using docker-compose with an env_file, these variables are already
# in the container's environment, so os.getenv() will pick them up.
# load_dotenv() here would primarily be for local development outside Docker
# or if you specifically point it to .env.gis.
load_dotenv()  # This will load from a file named '.env' by default if it exists.
# For the GIS setup, docker-compose's env_file directive handles .env.gis.

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
# Convert DEBUG to boolean, as os.getenv returns a string.
DEBUG_STR = os.getenv("DJANGO_DEBUG", "False")  # Default to "False" if not set
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
        # UPDATED: Environment variables to match your .env.gis for Azure
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
# Optional: Define STATIC_ROOT for collectstatic if you haven't already
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
        "rest_framework.authentication.BasicAuthentication",  # Consider TokenAuthentication for more robust API security
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",  # Changed for more flexibility
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    # Added default pagination for consistency
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,  # Default page size for pagination
    # Default filters path
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}

SPECTACULAR_SETTINGS = {
    "TITLE": "UXO Prioritization API",
    "DESCRIPTION": (
        "API backend for the UXO Prioritization and Risk Assessment System.\n\n"
        "This API allows users to:\n"
        "- View UXO records across regions\n"
        "- View regional GIS data with danger scores\n"  # Added this
        "- Filter/search by region, ordnance type, and condition\n"
        "- Generate visualized data-based reports built on different ML and statistical models\n"
        "- Create and manage UXO entries (authenticated users only)\n"
        "\nSecurity Note:\n"
        "Write operations (POST, PATCH, DELETE) require authentication."
    ),
    "VERSION": "1.0.0",
    "SCHEMA_PATH_PREFIX": "/api/v1",  # Ensure this matches your root API path
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SERIALIZER_EXTENSIONS": {
        "rest_framework_gis.fields.GeometryField": "drf_spectacular.extensions.OpenApiSerializerFieldExtension",
    },
    # DEFAULT_PAGINATION_CLASS and PAGE_SIZE are now in REST_FRAMEWORK settings
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "defaultModelRendering": "example",
        "defaultModelsExpandDepth": -1,  # Changed from 1 to -1 to collapse models by default
        "docExpansion": "none",  # list, full, or none
        "filter": True,
        "persistAuthorization": True,
    },
}

# GDAL and GEOS library paths (Usually not needed if system libraries are installed correctly and on PATH)
# However, if Django has trouble finding them, you might need to specify them.
# Check your Dockerfile ensures GDAL, GEOS, PROJ are installed.
# Example (uncomment and adjust if necessary, but try without first):
# GDAL_LIBRARY_PATH = '/usr/lib/libgdal.so' # Path might vary
# GEOS_LIBRARY_PATH = '/usr/lib/libgeos_c.so' # Path might vary
