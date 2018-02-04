import django


def pytest_configure(config):
    """Configure settings for testing reusable app"""
    from django.conf import settings

    settings.configure(
        PRODUCT_MODEL='tests.ProductModel',
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:'
            }
        },
        TEMPLATES=[
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'APP_DIRS': True,
                'OPTIONS': {
                    'debug': True,  # We want template errors to raise
                    'context_processors': [
                        'django.contrib.auth.context_processors.auth',
                    ]
                }
            },
        ],
        SECRET_KEY='not very secret in tests',
        USE_I18N=True,
        STATIC_URL='/static/',
        ROOT_URLCONF='tests.urls',
        MIDDLEWARE=(
            'django.middleware.common.CommonMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ),
        INSTALLED_APPS=(
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.sites',
            'django.contrib.staticfiles',
            'shoppingcart.apps.ShoppingcartConfig',
            'tests',
        ),
        PASSWORD_HASHERS=(
            'django.contrib.auth.hashers.MD5PasswordHasher',
        ),
    )

    django.setup()
