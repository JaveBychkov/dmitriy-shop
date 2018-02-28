from .base import *  # NOQA


DEBUG = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mptt',

    'profiles.apps.ProfilesConfig',
    'onlineshop.apps.OnlineshopConfig',
    'shoppingcart.apps.ShoppingcartConfig',
    'orders.apps.OrdersConfig',
    'remindme.apps.RemindMeConfig',
    'history.apps.HistoryConfig',
    'feedback.apps.FeedbackConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CELERY_TASK_ALWAYS_EAGER = True