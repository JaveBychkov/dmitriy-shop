import pytest

from onlineshop.tests.factories import product_factory

from shoppingcart.signals import price_changed, price_changed_callback
from shoppingcart.models import Cart, Line


def handler(sender, product, **kwargs):
    sender.called = True
    sender.product = product


@pytest.mark.django_db
class TestSignals:

    def test_signal_sends_with_product_argument(self):

        product = product_factory(price=1000, discount=5)

        price_changed.connect(handler)

        price_changed.send(self.__class__, product=product)

        assert self.called
        assert self.product == product

    def test_price_changed_callback_modify_line_object(self):
        """
        Test that price_changed_callback will modify price_changed
        field on all shopping cart lines that contain passed product.
        """
        cart = Cart.objects.create()
        product = product_factory(price=1000, discount=5)
        line = Line.objects.create(cart=cart, product=product)

        price_changed.connect(price_changed_callback)

        price_changed.send(self.__class__, product=product)

        line.refresh_from_db()

        assert line.price_changed
