import pytest

from onlineshop.models import (Product, Category, Attribute,
                               ProductAttributeValue)

from .factories import (product_factory, category_factory, attribute_factory,
                        product_attribute_value_factory)


class TestProductFactory:
    def test_returns_instance(self):
        p = product_factory(to_db=False)
        assert isinstance(p, Product)

    @pytest.mark.django_db
    def test_instance_save_to_db(self):
        p = product_factory()
        assert getattr(p, 'pk', None) is not None

    @pytest.mark.django_db
    def test_instance_and_category_instance_will_be_saved_to_db(self):
        p = product_factory()
        assert getattr(p.category, 'pk', None) is not None


class TestCategoryFactory:

    def test_returns_instance(self):
        c = category_factory(to_db=False)
        assert isinstance(c, Category)

    @pytest.mark.django_db
    def test_instance_save_to_db(self):
        c = category_factory()
        assert getattr(c, 'pk', None) is not None

    def test_instance_with_custom_attributes(self):
        c = category_factory(title='Hats', to_db=False)
        assert c.title == 'Hats'

    def test_create_instance_with_linked_category(self):
        c = category_factory(
            parent=category_factory(
                title='Winter', to_db=False), to_db=False)
        assert c.parent.title == 'Winter'


class TestAttributeFactory:

    def test_returns_instance(self):
        a = attribute_factory(to_db=False)
        assert isinstance(a, Attribute)

    @pytest.mark.django_db
    def test_instance_save_to_db(self):
        a = attribute_factory()
        assert getattr(a, 'pk', None) is not None

    def test_instance_with_custom_attributes(self):
        a = attribute_factory(name='Resolution', to_db=False)
        assert a.name == 'Resolution'


class TestProductAttributeValueFactory:

    def test_returns_instance(self):
        pav = product_attribute_value_factory(to_db=False)
        assert isinstance(pav, ProductAttributeValue)

    @pytest.mark.django_db
    def test_instance_save_to_db(self):
        pav = product_attribute_value_factory(
            product=product_factory(), attribute=attribute_factory()
        )
        assert getattr(pav, 'pk', None) is not None

    def test_instance_with_custom_attribytes(self):
        pav = product_attribute_value_factory(value='Blue', to_db=False)
        assert pav.value == 'Blue'
