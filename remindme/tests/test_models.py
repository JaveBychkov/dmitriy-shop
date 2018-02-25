import pytest
from django.db import IntegrityError

from onlineshop.tests.factories import product_factory

from remindme.models import Reminder


@pytest.mark.django_db
def test_cant_have_two_identical_remindedrs():
    product = product_factory()

    Reminder.objects.create(product=product, email='example@mail.com')

    # Test allows save for different email.
    Reminder.objects.create(product=product, email='example2@mail.com')

    with pytest.raises(IntegrityError):
        Reminder.objects.create(product=product, email='example@mail.com')
