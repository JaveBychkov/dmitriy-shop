from django.apps import AppConfig

from .signals import product_in_stock, product_in_stock_callback


class RemindMeConfig(AppConfig):
    name = 'remindme'

    def ready(self):
        product_in_stock.connect(product_in_stock_callback)
