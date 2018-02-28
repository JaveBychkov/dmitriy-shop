import datetime
from unittest.mock import patch

import pytest
from django.utils import timezone
from django.urls import reverse

from onlineshop.views import (CategoryDetailView, OnlineShopHomePageView,
                              ProductDetailView)

from .factories import (attribute_factory, category_factory,
                        product_attribute_value_factory, product_factory)

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
        view = CategoryDetailView(request=request, object=category)

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

        view = CategoryDetailView(request=request, object=category)

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


def test_product_detail_view_ordering(client, settings):
    product_factory(discount=10)

    test_time = timezone.now() - datetime.timedelta(days=60)

    with patch('django.utils.timezone.now') as date_mock:
        date_mock.return_value = test_time
        product_factory(discount=20)

    url_discount = '{}?order=discount'.format(reverse('onlineshop:home'))
    url_new = '{}?order=new'.format(reverse('onlineshop:home'))

    response = client.get(url_discount)

    assert response.status_code == 200
    products = response.context['products']
    assert products[0].discount > products[1].discount
    assert products[0].discount == 20

    response = client.get(url_new)
    assert response.status_code == 200
    products = response.context['products']
    assert products[0].date_added > products[1].date_added
    assert products[1].date_added == test_time
