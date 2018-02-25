import json

import pytest
from django.http import Http404
from django.urls import reverse
from django.utils import translation

from onlineshop.tests.factories import product_factory
from remindme.models import Reminder
from remindme.views import add_reminder

pytestmark = pytest.mark.django_db


@pytest.fixture
def product_in_stock():
    return product_factory()


@pytest.fixture
def product_out_of_stock():
    return product_factory(stock=0)


@pytest.fixture
def valid_request(rf, product_out_of_stock):
    p = product_out_of_stock
    request = rf.post(
        '/',
        json.dumps({'product': p.pk, 'email': 'example@mail.com'}),
        content_type='application/json',
        HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    return request


@pytest.fixture
def invalid_request(rf, product_in_stock):
    p = product_in_stock
    request = rf.post(
        '/',
        json.dumps({'product': p.pk, 'email': 'example@mail.com'}),
        content_type='application/json',
        HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    return request


@pytest.fixture
def ignore_404_warning():
    """
    Fixture to ignore 404 Not Found warning that shows up in some tests that
    test 404 status code is returned.
    """
    import logging
    logger = logging.getLogger('django.request')
    previous_level = logger.getEffectiveLevel()
    logger.setLevel(logging.ERROR)
    yield
    logger.setLevel(previous_level)


class TestAddReminderView:

    def test_adds_new_reminder(self, valid_request):
        """Test that new reminder adds successfully."""

        with translation.override('en'):
            response = add_reminder(valid_request)

        msg = 'We will notify you as soon as product will go on sale'
        data = json.loads(response.content)
        assert response.status_code == 200
        assert Reminder.objects.filter(email='example@mail.com').exists() is True
        assert msg in data['message']

    def test_dont_add_new_reminder_if_product_in_stock(self, invalid_request):
        """Test that new reminder will not be added if product in stock."""

        with translation.override('en'):
            response = add_reminder(invalid_request)

        msg = 'Something went wrong, try again later'
        data = json.loads(response.content)
        assert response.status_code == 404
        assert Reminder.objects.exists() is False
        assert msg in data['message']

    def test_request_not_ajax(self, rf):
        request = rf.post('/', data={})

        with pytest.raises(Http404):
            add_reminder(request)


# Using django client

class TestAddReminderViewUsingDjangoClient:

    def test_adds_new_reminder(self, product_out_of_stock, client):
        p = product_out_of_stock

        response = client.post(
            reverse('add-reminder'),
            json.dumps({'product': p.pk, 'email': 'example@mail.com'}),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        assert response.status_code == 200
        assert Reminder.objects.filter(email='example@mail.com').exists() is True

    def test_add_if_product_in_stock(self, product_in_stock, client,
                                     ignore_404_warning):
        p = product_in_stock

        response = client.post(
            reverse('add-reminder'),
            json.dumps({'product': p.pk, 'email': 'example@mail.com'}),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        assert response.status_code == 404
        assert Reminder.objects.exists() is False

    def test_non_ajax_request(self, client, ignore_404_warning):
        response = client.post(reverse('add-reminder'), {})
        assert response.status_code == 404
