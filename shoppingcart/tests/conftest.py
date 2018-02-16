import json
import pytest

from django.contrib.auth.models import AnonymousUser

from onlineshop.tests.factories import product_factory


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


@pytest.fixture
def product():
    return product_factory(
        price=1000, discount=0, slug='some-some', stock=5
    )
