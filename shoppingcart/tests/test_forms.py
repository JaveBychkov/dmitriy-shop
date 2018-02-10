import pytest

from onlineshop.tests.factories import product_factory

from shoppingcart.models import Cart, Line
from shoppingcart.forms import BaseForm, ProductForm


class TestBaseForm:

    def test_initialization(self):
        f = BaseForm(cart='some cart')

        assert f.cart == 'some cart'


@pytest.mark.django_db
class TestProductForm:

    def test_clean_passess(self):
        """
        Test that form clean method returns cleaned data if there is product
        with given id and slug in user shopping cart.
        """
        cart = Cart.objects.create()
        p1 = product_factory(
            slug='something-1', price='1000', discount='5'
        )
        Line.objects.create(product=p1, cart=cart)

        f = ProductForm(data={'id_': p1.pk, 'slug': p1.slug}, cart=cart)

        assert f.is_valid()
        assert all([x in f.cleaned_data for x in ['id_', 'slug']])

    def test_clean_fails(self):
        """
        Test that form clean method add errors to form if there is no product
        with given id and slug in user shopping cart.
        """
        cart = Cart.objects.create()

        f = ProductForm(
            data={'id_': 18, 'slug': 'some-slug'}, cart=cart
        )

        assert not f.is_valid()
        assert f.errors.get('__all__') is not None
