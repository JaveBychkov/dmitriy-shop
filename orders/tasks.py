import logging

from django.conf import settings
from django.core import mail

from config.celery import app

from .models import Order
from .utils import get_email_obj


@app.task
def send_order_placed_email(subject, context, templates):
    try:
        order = Order.objects.get(pk=context['order'])
        context['order'] = order
        with mail.get_connection() as connection:
            user_email = get_email_obj(
                subject, context, templates['user'], [order.email]
            )

            mail_to = [manager[1] for manager in settings.MANAGERS]
            managers_email = get_email_obj(
                subject, context, templates['manager'], mail_to
            )

            connection.send_messages([user_email, managers_email])

    except Order.DoesNotExist:
        logging.warning("Non existing order! {}".format(context['order']))
