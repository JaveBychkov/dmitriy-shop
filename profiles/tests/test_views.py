import pytest
from django.contrib.messages import constants
from django.urls import reverse

from shoppingcart.models import Cart, Line
from onlineshop.tests.factories import product_factory

from profiles.models import User
from profiles.views import CopySessionCartAfterLoginView


pytestmark = pytest.mark.django_db


@pytest.fixture()
def user():
    user = User.objects.create_user(
        'User1', 'user@mail.com', 'somepass', first_name='UserF',
        last_name='UserL'
    )
    user.address.country = 'Russia'
    user.address.save()
    return user


class TestUpdateProfileView:

    def test_login_required(self, client):
        response = client.get(reverse('profiles:detail'))
        # Redirect to login page.
        assert response.status_code == 302

    def test_get_request_returns_form_with_initials(self, client, user):
        initial = ['user@mail.com', 'UserF', 'UserL', 'Russia']
        client.force_login(user)
        response = client.get(reverse('profiles:detail'))
        content = response.content.decode('utf-8')
        assert response.status_code == 200
        assert list(response.context['messages']) == []
        assert all([x in content for x in initial])

    def test_valid_post_request_changes_data(self, client, user):
        adr_payload = {'country': 'Russia', 'city': 'Nijniy-Novgorod',
                       'street': 'Rodionova', 'postcode': '123456',
                       'apartment': '24', 'house': '5'}

        usr_payload = {'first_name': 'UserF', 'last_name': 'NewLastName',
                       'email': 'user@mail.com'}
        payload = {**adr_payload, **usr_payload}

        client.force_login(user)

        response = client.post(
            reverse('profiles:detail'), payload, follow=True
        )

        messages = list(response.context['messages'])

        user.refresh_from_db()
        assert response.status_code == 200
        assert all(
            [getattr(user.address, x) == adr_payload[x] for x in adr_payload]
        )
        assert user.last_name == usr_payload['last_name']
        assert len(messages) == 1
        assert messages[0].level == constants.SUCCESS

    def test_invalid_post_request_donct_change_data(self, client, user):
        adr_payload = {'country': 'Germany'}

        usr_payload = {'first_name': 'UserF', 'last_name': 'NewLastName',
                       'email': 'user@mail.com'}

        payload = {**adr_payload, **usr_payload}

        client.force_login(user)

        response = client.post(
            reverse('profiles:detail'), payload, follow=True
        )

        messages = list(response.context['messages'])

        user.refresh_from_db()

        assert response.status_code == 200
        assert user.address.country != adr_payload['country']
        assert user.last_name != usr_payload['last_name']
        assert len(messages) == 1
        assert messages[0].level == constants.ERROR


class TestCopySessionCartAfterLoginView:

    def test_copy_session_view_adds_products(self, client, user):
        """Test that products from session carts got copied in user's cart"""
        cart = Cart.objects.create()
        Line.objects.create(product=product_factory(), cart=cart)

        session = client.session
        session['cart_id'] = cart.pk
        session.save()

        response = client.post(
            reverse('profiles:login'),
            {'username': 'User1', 'password': 'somepass'}
        )

        user.refresh_from_db()
        assert response.status_code == 302
        assert Cart.objects.count() == 2
        assert user.cart.line_set.count() == 1

    def test_copy_session_view_remove_duplicates(self, client, user, settings):
        p1 = product_factory(title='Phone')
        p2 = product_factory(title='PC')
        cart = Cart.objects.create()
        Line.objects.create(product=p1, cart=cart)
        Line.objects.create(product=p2, cart=cart)

        user_cart = Cart.objects.create(owner=user)
        Line.objects.create(product=p1, cart=user_cart)

        session = client.session
        session['cart_id'] = cart.pk
        session.save()

        # Change login redirect url so our test don't fail on rendering
        # template when trying to access unexisting image on product.
        # pytest-django mark: pytest.mark.ignore_template_errors - not working.
        settings.LOGIN_REDIRECT_URL = reverse('profiles:detail')

        response = client.post(
            reverse('profiles:login'),
            {'username': 'User1', 'password': 'somepass'},
            follow=True
        )

        assert response.status_code == 200
        assert Cart.objects.count() == 2
        assert user.cart.line_set.count() == 2
