from unittest.mock import patch

import pytest

from onlineshop.tests.factories import product_factory

from remindme.signals import product_in_stock, product_in_stock_callback


def handler(sender, product, request, **kwargs):
    sender.called = True
    sender.product = product
    sender.request = request


@pytest.mark.django_db
class TestRemindMeSignals:

    def test_signals_sends_with_required_arguments(self, rf):

        product = product_factory()
        request = rf.post('/')

        product_in_stock.connect(handler)

        product_in_stock.send(self.__class__, product=product, request=request)

        assert getattr(self, 'called', False) is True
        assert getattr(self, 'product', False) == product
        assert getattr(self, 'request', False) == request

    def test_callback_calls_celery_task(self, rf):
        """Test that signal starts celery task with right arguments"""
        product = product_factory()
        request = rf.post('/')

        url = request.build_absolute_uri(product.get_absolute_url())

        with patch('remindme.tasks.send_notification_email.delay') as task:
            product_in_stock_callback(
                self.__class__, product=product, request=request
            )
            task.assert_called_with(product.pk, product.title, url)
