import pytest

from django.core.exceptions import ValidationError

from shoppingcart.models import Cart, Line
from shoppingcart.forms import BaseForm, ProductForm


class TestBaseForm:

    def test_initialization(self):
        f = BaseForm(cart='some cart')

        assert f.cart == 'some cart'
        assert f.cached_product is None


@pytest.mark.django_db
class TestProductForm:

    def test_clean_passess(self, product):
        """
        Test that form clean method returns cleaned data if there is product
        with given id and slug in user shopping cart.
        """
        cart = Cart.objects.create()

        cart.add_product(product)

        f = ProductForm(data={'id_': product.pk}, cart=cart)

        assert f.is_valid() is True
        assert 'id_' in f.cleaned_data

    def test_clean_fails(self):
        """
        Test that form clean method add errors to form if there is no product
        with given id in user shopping cart.
        """
        cart = Cart.objects.create()

        f = ProductForm(
            data={'id_': 18}, cart=cart
        )

        assert f.is_valid() is False
        assert f.errors.get('__all__') is not None

    def test_clean_sets_cached_product_attribute(self, product):
        cart = Cart.objects.create()

        cart.add_product(product)

        f = ProductForm(data={'id_': product.pk}, cart=cart)

        assert f.is_valid() is True
        assert f.cached_product == product

    def test_get_product_returns_product(self):
        f = ProductForm(cart='cart')
        assert f.get_product() is None
        f.cached_product = 'Product'
        assert f.get_product() == 'Product'

    def test_check_product_in_cart_raise_error(self):
        """Raise error if product not in user cart"""
        cart = Cart.objects.create()
        f = ProductForm(data={'id_': 1}, cart=cart)
        with pytest.raises(ValidationError):
            f.check_product_in_cart()

    def test_check_product_in_cart_not_raises_error(self, product):
        cart = Cart.objects.create()
        cart.add_product(product)
        f = ProductForm(data={'id_': product.pk}, cart=cart)
        f.cached_product = product
        f.check_product_in_cart()
        # No assertions required
