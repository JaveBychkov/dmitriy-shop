import pytest

from onlineshop.views import (CategoryDetailView,
                              ProductDetailView, OnlineShopHomePageView)

from .factories import (category_factory, product_factory, attribute_factory,
                        product_attribute_value_factory)


pytestmark = pytest.mark.django_db


class TestCategoryDetailView:

    def test_category_detail_view_return_200(self, rf):
        category = category_factory()

        request = rf.get('/')

        response = CategoryDetailView.as_view()(request, slug=category.slug)

        assert response.status_code == 200

    def test_category_detail_view_get_context_data(self, rf):
        category = category_factory()

        for i in range(12):
            product_factory(category=category)

        request = rf.get('/')
        response = CategoryDetailView.as_view()(request, slug=category.slug)

        assert 'products' in response.context_data
        assert len(response.context_data['products']) == 6

    def test_category_detail_view_get_paginator(self, rf):
        category = category_factory()

        for i in range(12):
            product_factory(category=category)

        request = rf.get('/')
        view = CategoryDetailView()
        view.request = request
        view.object = category

        page = view.get_paginator()
        paginator = page.paginator

        assert paginator.count == 12
        assert paginator.num_pages == 2
        assert page.number == 1
        assert page.has_next()

    def test_category_detail_view_get_paginator_page_in_request(self, rf):
        category = category_factory()

        for i in range(12):
            product_factory(category=category)

        request = rf.get('/')

        # Immutable QueryDict to mutable.
        request.GET = request.GET.copy()
        request.GET['page'] = 2

        view = CategoryDetailView()
        view.request = request
        view.object = category

        page = view.get_paginator()
        paginator = page.paginator

        assert paginator.count == 12
        assert paginator.num_pages == 2
        assert page.number == 2
        assert not page.has_next()


def test_home_page_view(rf):
    request = rf.get('/')

    response = OnlineShopHomePageView.as_view()(request)

    assert response.status_code == 200


def test_product_detail_view(rf, django_assert_num_queries):
    product = product_factory()
    attribute = attribute_factory(name='Color')
    product_attribute_value_factory(product=product, attribute=attribute)

    request = rf.get('/')

    response = ProductDetailView.as_view()(request, slug=product.slug)

    assert response.status_code == 200
    context = response.context_data
    assert 'attributes' in context
    attr = context['attributes'][0]
    with django_assert_num_queries(1):
        assert attr.product == product
        assert attr.attribute == attribute
