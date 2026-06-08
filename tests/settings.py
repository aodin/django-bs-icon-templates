"""Minimal Django settings for the test suite."""

SECRET_KEY = "test-secret-key"

INSTALLED_APPS = [
    "bs_icon_templates",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {},
    },
]

USE_TZ = True

BASE_DIR = "."
