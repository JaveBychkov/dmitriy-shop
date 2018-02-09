import pytest

from shoppingcart.models import Cart, Line

from .models import ProductModel


pytestmark = pytest.mark.django_db


class TestCartModel:

    def test_product_in_cart_method(self):
        p = ProductModel.objects.create(price=1, discount=0)
        cart = Cart.objects.create()
        Line.objects.create(cart=cart, product=p)

        assert cart.product_in_cart(p)


class TestLineModel:

    def test_total_price_method(self):
        p = ProductModel.objects.create(price=2, discount=0)
        cart = Cart.objects.create()
        line = Line.objects.create(cart=cart, product=p)

        assert line.total_price() == 2
