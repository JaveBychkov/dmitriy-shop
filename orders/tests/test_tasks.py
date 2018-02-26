from unittest.mock import patch

import pytest

from orders.models import Order
from orders.tasks import send_order_placed_email

pytestmark = pytest.mark.django_db


def test_log_if_no_order_exists():
    order = 2
    message = 'Non existing order! {}'.format(order)
    with patch('orders.tasks.logging.warning') as warning:
        send_order_placed_email(1, {'order': order}, 'sometemplates')
        warning.assert_called_with(message)


def test_sends_two_emails(mailoutbox, settings, form_data):
    settings.MANAGERS = (('manager', 'manager@mail.com'),)

    order = Order.objects.create_order_instance(form_data)
    order.save()

    context = {'order': order.pk}
    templates = {'user': 'orders/emails/email_for_user.html',
                 'manager': 'orders/emails/email_for_manager.html'}

    send_order_placed_email('Order placed', context, templates)

    assert len(mailoutbox) == 2
    assert ['manager@mail.com'] in [m.to for m in mailoutbox]
    assert ['email@email.com'] in [m.to for m in mailoutbox]
