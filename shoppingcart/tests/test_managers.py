import pytest

from shoppingcart.models import Cart


# u_request - Authenticated request.
# a_request - Anonymous request.
# See conftest.py


pytestmark = pytest.mark.django_db


class TestCartManager:

    def test_get_cart_creates_new_cart_for_user(self, u_request):
        user_and_session = u_request.user, u_request.session
        cart = Cart.objects.get_cart(*user_and_session)
        assert hasattr(cart, 'pk')
        assert Cart.objects.count() == 1
        assert hasattr(u_request.user, 'cart')
        assert cart == u_request.user.cart

    def test_get_cart_returns_existing_cart_for_user(self, u_request):
        user_and_session = u_request.user, u_request.session
        existing_cart = Cart.objects.create(owner=u_request.user)
        cart = Cart.objects.get_cart(*user_and_session)
        assert existing_cart == cart
        assert Cart.objects.count() == 1

    def test_get_session_cart_called_if_not_authenticated(self, a_request):
        user_and_session = a_request.user, a_request.session

        def get_session_cart(self, *args, **kwargs):
            self.session_cart_called = True

        # Save original method to a variable, otherwise following tests will
        # fail
        original_method = Cart.objects.get_session_cart

        # Use fake method just to make sure it's being called.
        # https://docs.python.org/3.6/howto/descriptor.html#functions-and-methods
        Cart.objects.get_session_cart = get_session_cart.__get__(Cart.objects)
        Cart.objects.get_cart(*user_and_session)

        # Return original method
        Cart.objects.get_session_cart = original_method

        assert Cart.objects.session_cart_called is True

    def test_create_session_cart_creates_session_cart(self, a_request):
        """Test that id of just created cart was written to a session"""
        session = a_request.session
        cart = Cart.objects.create_session_cart(session)
        assert hasattr(cart, 'pk')
        assert a_request.session.get('cart_id') == cart.pk

    def test_get_session_cart_returns_new_cart_for_guest(self, a_request):
        user_and_session = a_request.user, a_request.session

        cart = Cart.objects.get_session_cart(*user_and_session)
        assert hasattr(cart, 'pk')
        assert a_request.session.get('cart_id') == cart.pk

    def test_get_session_cart_returns_existing_cart_for_guest(self, a_request):
        user_and_session = a_request.user, a_request.session

        existing_cart = Cart.objects.create()
        a_request.session['cart_id'] = existing_cart.pk
        cart = Cart.objects.get_session_cart(*user_and_session)
        assert cart.pk == existing_cart.pk
        assert Cart.objects.count() == 1

    def test_get_session_cart_returns_new_cart_if_no_cart(self, a_request):
        """"
        Test that get_session_cart will return new cart for user if cart
        with id that was written to user session was removed for some reason/
        """
        user_and_session = a_request.user, a_request.session

        a_request.session['cart_id'] = 105
        cart = Cart.objects.get_session_cart(*user_and_session)
        assert a_request.session['cart_id'] == cart.pk
        assert Cart.objects.count() == 1

    def test_get_full_cart_call_get_cart_with_custom_qs(self, u_request):
        user_and_session = u_request.user, u_request.session

        def get_cart(self, user, session, queryset=None):
            self.passed_queryset = queryset

        original_method = Cart.objects.get_cart
        # https://docs.python.org/3.6/howto/descriptor.html#functions-and-methods
        Cart.objects.get_cart = get_cart.__get__(Cart.objects)
        Cart.objects.get_full_cart(*user_and_session)

        Cart.objects.get_cart = original_method

        assert Cart.objects.passed_queryset is not None
