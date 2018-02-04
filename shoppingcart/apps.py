from django.apps import AppConfig

from .signals import price_changed, price_changed_callback


class ShoppingcartConfig(AppConfig):
    name = 'shoppingcart'

    def ready(self):
        price_changed.connect(price_changed_callback)
