import json

import pytest
from django.contrib.auth.models import AnonymousUser

from onlineshop.tests.factories import product_factory
from shoppingcart.models import Cart, Line


@pytest.fixture
def form_data():
    form_data = {'user':
                 {'first_name': 'first_name', 'last_name': 'last_name',
                  'email': 'email@email.com'},
                 'address':
                 {'country': 'country', 'city': 'city',
                  'street': 'street', 'postcode': 'postcode',
                  'house': 'house', 'apartment': 'apartment'}
                 }
    return form_data


@pytest.fixture
def cart_w_items():
    cart = Cart.objects.create()
    Line.objects.bulk_create([
        Line(cart=cart, product=product_factory(price=1000)),
        Line(cart=cart, product=product_factory(price=2000)),
        Line(cart=cart, product=product_factory(price=3000)),
    ])
    return cart


@pytest.fixture
def user_w_cart(cart_w_items, admin_user):
    cart_w_items.owner = admin_user
    cart_w_items.save()
    return admin_user


@pytest.fixture
def session_request(rf):
    """Don't actually session, just interface that some methods needs"""
    request = rf.post(
        '/', json.dumps({'id_': '2'}), content_type='application/json'
    )
    request.session = {}
    return request


@pytest.fixture
def a_request(session_request):
    """AnonymousUser request"""
    session_request.user = AnonymousUser()
    return session_request


@pytest.fixture
def u_request(session_request, admin_user):
    """Authenticated request"""
    session_request.user = admin_user
    return session_request
