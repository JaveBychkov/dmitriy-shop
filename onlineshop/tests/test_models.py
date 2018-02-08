from decimal import Decimal
from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError

from onlineshop.models import image_upload_path

from .factories import product_factory, category_factory, attribute_factory


@patch('onlineshop.models.uuid')
def test_upload_image_path(uuid_mock):
    uuid_mock.uuid4.return_value = 'fddb8ee8-74ce-45db-bb4d-387bf8cc488d'
    expected_output = 'fd/db/8ee8-74ce-45db-bb4d-387bf8cc488d.jpg'
    assert expected_output == image_upload_path('instance', 'imageFile.jpg')


class TestProductModel:
    def test_string_representation(self):
        p = product_factory(title='Something', to_db=False)
        assert str(p) == 'Something'

    def test_in_stock(self):
        p = product_factory(title='Something', stock=1, to_db=False)
        assert p.in_stock() == 1

    def test_not_in_stock(self):
        p = product_factory(title='Something', stock=0, to_db=False)
        assert p.in_stock() == 0

    def test_admin_in_stock_returns_bool(self):
        p = product_factory(title='Something', stock=23, to_db=False)
        assert p._in_stock_admin() is True

    def test_minimal_price(self):
        p = product_factory(price=Decimal(-10.00), to_db=False)
        with pytest.raises(ValidationError):
            p.clean_fields()

    def test_maximum_discount(self):
        p = product_factory(discount=100, to_db=False)
        with pytest.raises(ValidationError):
            p.clean_fields()

    @pytest.mark.django_db
    def test_default_category(self):
        p = product_factory(add_category=False)
        assert p.category.title == 'Unassigned'

    def test_price_with_discount(self):
        p = product_factory(price=Decimal(3600.00), discount=10, to_db=False)
        assert p.get_price() == 3240.00

    def test_price_without_discount(self):
        p = product_factory(price=Decimal(3600.00), discount=0, to_db=False)
        assert p.get_price() == p.price

    def test_get_absolute_url(self):
        p = product_factory(title='Some', slug='some', to_db=False)
        assert p.get_absolute_url() == '/products/some'


class TestCategoryModel:
    def test_string_representation(self):
        c = category_factory(title='Something', to_db=False)
        assert str(c) == 'Something'

    @pytest.mark.django_db
    def test_get_all_products(self):
        c = category_factory(title='RootCategory')
        b = category_factory(title='SubCategory', parent=c)
        p1 = product_factory(category=c)
        p2 = product_factory(category=b)

        assert set(c.get_all_products()) == set([p1, p2])


class TestAttributeModel:

    def test_string_representation(self):
        a = attribute_factory(name='Resolution', to_db=False)
        assert str(a) == 'Resolution'
