import pytest
from django.utils import translation

from onlineshop.tests.factories import product_factory

from remindme.models import Reminder
from remindme.tasks import send_notification_email


pytestmark = pytest.mark.django_db


def test_email_not_sent_if_no_recipients(mailoutbox):
    send_notification_email(10, 'Title', 'SomeUrl')

    assert len(mailoutbox) == 0


def test_email_with_notification_sent(mailoutbox):
    product = product_factory(stock=0)
    Reminder.objects.create(product=product, email='example@mail.com')
    Reminder.objects.create(product=product, email='example2@mail.com')

    with translation.override('en'):
        send_notification_email(product.pk, product.title, 'SomeUrl')

    assert len(mailoutbox) == 1
    m = mailoutbox[0]
    assert m.subject == '{} have gone on sale!'.format(product.title)
    assert product.title in m.body
    assert set(m.to) == {'example@mail.com', 'example2@mail.com'}


def test_reminders_deleted_after_mail_sent(mailoutbox):
    product = product_factory(stock=0)
    Reminder.objects.create(product=product, email='example@mail.com')
    Reminder.objects.create(product=product, email='example2@mail.com')

    send_notification_email(product.pk, product.title, 'SomeUrl')

    assert Reminder.objects.exists() is False
