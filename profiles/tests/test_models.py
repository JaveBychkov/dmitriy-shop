import pytest

from profiles.models import User


@pytest.mark.django_db
def test_address_creation_for_user():
    u = User.objects.create_user('User1', 'user@user.com', 'somepass')
    assert hasattr(u, 'address')


@pytest.mark.django_db
def test_user_has_address_method():
    u = User.objects.create_user('User1', 'user@user.com', 'somepass')
    assert u.has_address()
    u.address.delete()
    u.refresh_from_db()
    assert u.has_address() is False
