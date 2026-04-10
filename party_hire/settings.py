import os
from pathlib import Path
from decouple import config
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'crispy_forms',
        'crispy_bootstrap4',
        'django_extensions',

        'apps.core',
        'apps.items',
        'apps.bookings',
        'apps.contact',

]

MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'apps.core.middleware.ThemeMiddleware',
        'apps.core.middleware.ThemeContextMiddleware',
]

ROOT_URLCONF = 'party_hire.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.theme_context',
            ],
        },
    },

]

WSGI_APPLICATION = 'party_hire.wsgi.application'

# Database
DATABASES = {
        'default': dj_database_url.config(default=config('DATABASE_URL'))

}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
        {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
        {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
        {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
        {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},

]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"
CRISPY_TEMPLATE_PACK = "bootstrap4"

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Theme settings
AVAILABLE_THEMES = ['default', 'elegant', 'modern']
ACTIVE_THEME = 'default'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Stripe (for deposits)
STRIPE_PUBLIC_KEY = config('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY')

# Theme settings (add to your existing settings)
AVAILABLE_THEMES = {
    'default': {
        'name': 'Classic Blue',
        'description': 'Clean and professional blue theme',
        'css_file': 'css/themes/default/style.css',
        'thumbnail': 'themes/default-thumb.jpg'
    },
    'elegant': {
        'name': 'Elegant Gold',
        'description': 'Luxurious gold and dark theme for premium events',
        'css_file': 'css/themes/elegant/style.css',
        'thumbnail': 'themes/elegant-thumb.jpg'
    },
    'modern': {
        'name': 'Modern Gradient',
        'description': 'Contemporary gradient design with vibrant colors',
        'css_file': 'css/themes/modern/style.css',
        'thumbnail': 'themes/modern-thumb.jpg'
    }
}
ACTIVE_THEME = 'default'  # Can be changed via session or user preference

