import pytest
from django.utils import translation

from orders.models import Order

pytestmark = pytest.mark.django_db


@pytest.fixture
def order(form_data):
    with translation.override('en'):
        return Order.objects.create_order_instance(form_data)


class TestOrderModel:

    def test_string_representation_method(self):

        order = Order()
        order.pk = 2
        with translation.override('en'):
            assert str(order) == 'Order# 2'

    def test_from_cart_to_order_fill_order_instance(self, cart_w_items, order):
        order.from_cart_to_order(cart_w_items)

        assert order.total == 6000
        assert order.products.count() == 3
        assert cart_w_items.line_set.exists() is False
        assert order.user is None

        # Check that ammout of items in stock changed, our products by default
        # has 126 items in stock, so it should be 125 now.

        for line in order.products.all():
            assert line.product.stock == 125

    def test_order_associates_with_user(self, user_w_cart, order):
        """
        Test that order will be associated with user if passed tp
        .from_cart_to_order() cart have owner.
        """
        cart = user_w_cart.cart

        order.from_cart_to_order(cart)

        assert order.user == user_w_cart

    def test_create_order_from_form_data(self, order):
        assert order.email == 'email@email.com'
        assert order.full_name == 'first_name last_name'
        assert order.address == (
            'country, city, street, postcode, h.house, ap.apartment'
        )