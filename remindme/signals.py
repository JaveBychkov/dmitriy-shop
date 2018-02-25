from django.dispatch import Signal


product_in_stock = Signal(providing_args=['product', 'request'])


def product_in_stock_callback(sender, product, request, **kwargs):
    # Avoid "Apps not loaded yet" error
    from .tasks import send_notification_email

    url = request.build_absolute_uri(product.get_absolute_url())
    # Celery task.
    send_notification_email.delay(product.pk, product.title, url)
