from django.dispatch import Signal


price_changed = Signal(providing_args=['product'])


def price_changed_callback(sender, product, **kwargs):
    """
    Signal handler that changes all associated with product Line objects
    attributes .price_changed to True.

    You should use it if you want warning message about changed price to appear
    on user's shoppingcart detail apge.

    If you want to use this handler import signal:
    `from shoppingcart.signals import price_changed`
    And send it whenever you change the price of product.
    For example in admin on model save:

        class ProductAdmin(admin.ModelAdmin):

            def save_model(self, request, obj, form, change):
                data = form.changed_data

                if any([x in data for x in ['price', 'discount']]):
                    price_changed.send(sender=self.__class__, product=obj)

                super().save_model(request, obj, form, change)


    Parameters:
    -----------
    sender : object
        Sender of price_changed signal.
    product : models.Model
        Instance of PRODUCT_MODEL defined in settings.PRODUCT_MODEL

    Returns:
    --------
    None
    """
    product.line_set.update(price_changed=True)
