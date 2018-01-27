from unittest.mock import MagicMock

import pytest

from django.contrib.admin.sites import AdminSite

from onlineshop.admin import ProductAdmin
from onlineshop.models import Product

from .factories import product_factory


@pytest.fixture
def model_admin():
    site = AdminSite()
    return ProductAdmin(Product, site)


@pytest.fixture()
def products_qs():
    for i in range(3):
        product_factory()
    return Product.objects.all()


@pytest.mark.django_db
def test_add_discount_action_default_page(model_admin, products_qs, rf):
    """
    Test that click on default django admin button to apply action will
    render our template and passed context will contain our products alongside
    with selected items.
    """
    # Can't use slice here because our action use .update to update qs.
    ids = list(products_qs.order_by('-id')[:2].values_list('id', flat=True))
    qs = products_qs.filter(id__in=ids)

    request = rf.post('/')
    # Convert immutable QueryDict to mutable by copying it.
    request.POST = request.POST.copy()
    # Update QueryDict to contain ID of products that should be changed.
    request.POST.setlist('_selected_action', ids)

    response = model_admin.add_discount(request, qs)

    form = response.context_data['form']

    assert response.status_code == 200
    assert response.context_data['products'] == qs
    assert form.initial['_selected_action'] == ids


@pytest.mark.django_db
def test_add_discount_action_intermediate_page(model_admin, products_qs, rf):
    """
    Test that applying changes on intermediate page will actually have
    the consequences.
    """
    ids = list(products_qs.order_by('-id')[:2].values_list('id', flat=True))
    qs = products_qs.filter(id__in=ids)

    request = rf.post('/s')
    # Convert immutable QueryDict to mutable by copying it.
    request.POST = request.POST.copy()
    # Update QueryDict to contain ID of products that should be changed.
    request.POST.setlist('_selected_action', ids)
    # Actual value from form on intermediate page.
    request.POST['apply'] = 'Apply discount'
    # Discount setted on intermediate page.
    request.POST['discount'] = 20

    model_admin.message_user = MagicMock()
    response = model_admin.add_discount(request, qs)

    updated_qs = Product.objects.all()
    with_discount = updated_qs.order_by('-id')[:2]

    assert response is None
    assert all([item.discount == 20 for item in with_discount])
    assert updated_qs[0].discount == 0
    model_admin.message_user.assert_called()
