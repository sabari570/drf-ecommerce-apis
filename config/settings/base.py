from pathlib import Path
from datetime import timedelta
# Config is used to access the .env values
# Csv is used to convert the values from .env as as list
from decouple import config, Csv
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

AUTH_USER_MODEL = 'users.CustomUser'


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party apps
    # this is added inorder to setup the django admin panel when the DB is postgres
    'django.contrib.sites',
    'rest_framework',
    'rest_framework.authtoken',
    'dj_rest_auth',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'django_countries',
    # For google login setup
    'allauth.socialaccount.providers.google',
    'dj_rest_auth.registration',
    'corsheaders',
    'rest_framework_simplejwt.token_blacklist',

    # for API documentation
    'drf_spectacular',

    # Local apps
    'users',
    'products',
    'cart',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USERNAME'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOSTNAME'),
        'PORT': config('DB_PORT', cast=int)
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'dj_rest_auth.jwt_auth.JWTCookieAuthentication',

        # This is the CustomJWTCookieAuthentication we created inorder to improve security
        'users.authenticate.CustomJWTCookieAuthentication',
    ),
    # Inorder to setup API documentation
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",

    # Adding pagination to the application,
    # Here the pagination style is via page numbers
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

# This is inorder to view the django admin panel
SITE_ID = 1

# Token length for OTP
TOKEN_LENGTH = 6

# Token expiry
TOKEN_EXPIRE_MINUTES = 3

# This line indicates use JWT for authentication
REST_USE_JWT = True
# This is the keyname in which the access token will be stored in the cookie
JWT_AUTH_COOKIE = 'phonenumber-auth'
# This is the keyname in which the refresh token will be stored in the cookie
JWT_AUTH_REFRESH_COOKIE = 'phonenumber-refresh-token'

# If set to True, the cookie will only be sent through https scheme. Default is False.
JWT_AUTH_SECURE = False
# If set to True, the client-side JavaScript will not be able to access the cookie. Default is True.
JWT_AUTH_HTTPONLY = True

# This is for the allauth setup
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'madatory'

# This is needed when the phone number needs to parsed while loggin in using phone number
PHONENUMBER_DEFAULT_REGION = 'ET'

# Django by default uses username/password-based authentication via ModelBackend.
# However, if you want to allow users to log in using their phone number or email,
# you need to create custom authentication backends and register them in AUTHENTICATION_BACKENDS inside settings.py.
# Since in this app we are logging in through email or phone number and password we customize the backends
# Create a folder like this: users/backend/email_backend
AUTHENTICATION_BACKENDS = [
    # This is the default that allows us to log in via username
    'django.contrib.auth.backends.ModelBackend',
    'users.backend.email_backend.EmailAuthBackend',
    'users.backend.phone_backend.PhoneNumberAuthBackend'
]

# This is set for the configuration of sending verification mails to the registered emails
# This setting is required only if you are actually sending emails to the registered users
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'your.email.host'
# EMAIL_USE_TLS = True
# EMAIL_PORT = 587
# EMAIL_HOST_USER = 'your email host user'
# EMAIL_HOST_PASSWORD = 'your email host password'

# In this case the email is sent and received by the console.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# After confirming the email you will be directed to this URL
LOGIN_URL = 'http://localhost:8000/api/user/login/'

# On setting this to true, when the password change API is HIT it will prompt you to enter the okd password
# inorder to change the password
OLD_PASSWORD_FIELD_ENABLED = True

# When password is changed it logs you out immediately when set to true
LOGOUT_ON_PASSWORD_CHANGE = True

# This configuration is for setting up the JWT token and blacklisting them
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,  # Blacklist old refresh tokens
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_BLACKLIST_ENABLED": True,
}

# Inorder to allow the requests from listed out domains
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Your frontend URL
]
# If your frontend needs to send credentials (e.g., cookies or authentication headers)
CORS_ALLOW_CREDENTIALS = True


# Inorder to setup API dodumentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'E-commerce API',
    'DESCRIPTION': 'An E-commerce API built using Django rest framework',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# Configuration to setup and view the media uploaded to the avatar folder
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
