import pytest

from onlineshop.tests.factories import product_factory

from shoppingcart.models import Cart, Line


pytestmark = pytest.mark.django_db


@pytest.fixture
def cart_w_items():
    cart = Cart.objects.create()
    Line.objects.bulk_create([
        Line(cart=cart, product=product_factory(price=1000)),
        Line(cart=cart, product=product_factory(price=2000)),
        Line(cart=cart, product=product_factory(price=3000)),
    ])
    return cart


class TestCartModel:

    def test_product_in_cart_method(self, cart_w_items):
        p = product_factory(price=1, discount=0)
        Line.objects.create(cart=cart_w_items, product=p)

        assert cart_w_items.product_in_cart(p)

    def test_get_total_price_method_returns_correct_price(self, cart_w_items):
        assert cart_w_items.get_total_price() == 6000

    def test_any_product_price_changed_method(self, cart_w_items):
        assert cart_w_items.any_product_price_changed() is False

        line = cart_w_items.line_set.first()
        line.price_changed = True
        line.save()

        assert cart_w_items.any_product_price_changed() is True

    def test_add_product_adds_product_to_cart(self, product):
        cart = Cart.objects.create()
        cart.add_product(product)
        assert cart.line_set.filter(product_id=product.pk).exists()

    def test_remove_product_removes_product_from_cart(self, product):
        cart = Cart.objects.create()
        Line.objects.create(cart=cart, product=product)

        assert cart.line_set.exists() is True
        cart.remove_product(product)
        assert cart.line_set.exists() is False

    def test_change_product_quantity_changes_quantity(self, product):
        cart = Cart.objects.create()
        Line.objects.create(cart=cart, product=product)

        cart.change_product_quantity(product, 4)

        assert cart.line_set.filter(quantity=4).exists()


class TestLineModel:

    def test_total_price_method(self):
        p = product_factory(price=2, discount=0)
        cart = Cart.objects.create()
        line = Line.objects.create(cart=cart, product=p)

        assert line.total_price() == 2
