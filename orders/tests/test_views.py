import pytest
from unittest.mock import patch
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.urls import reverse
from django.utils import translation

from orders.models import Order
from orders.views import (CheckOrderView, NotEmptyCartRequiredMixin,
                          PlaceOrderView)
from shoppingcart.models import Cart

pytestmark = pytest.mark.django_db


@pytest.fixture
def user_client(client, form_data, user_w_cart):
    """
    Fixture that provide client with logined user that have associated cart,
    form_data for order creation written to session.
    """
    session = client.session
    session['form'] = form_data
    session.save()
    client.force_login(user_w_cart)
    return client


class TestNotEmptyCartRequiredMixin:

    class DummyView:
        def dispatch(self, request, *args, **kwargs):
            self.parent_dispatch_called = True

    class AnotherDummyView(NotEmptyCartRequiredMixin, DummyView):
        def __init__(self, request):
            self.request = request

    def test_cart_not_empty(self, cart_w_items, u_request):
        """
        Test that if cart is not empty parent dispatch method would be called
        and user cart would be attached to view instance.
        """
        cart_w_items.owner = u_request.user
        cart_w_items.save()

        view = self.AnotherDummyView(u_request)
        view.dispatch(u_request)

        assert view.parent_dispatch_called is True
        assert hasattr(view, 'cart')
        assert view.cart == cart_w_items

    def test_cart_is_empty(self, u_request):
        """
        Test that if cart is empty parent dispatch method would not be called
        and redirect would be returned + error message attached to request.
        """
        # It seems that Request Factory not setting _messages attribute and
        # test fails with error saying that Messages Framework not installed,
        # fix from SO below.
        u_request._messages = FallbackStorage(u_request)

        Cart.objects.create(owner=u_request.user)

        view = self.AnotherDummyView(u_request)
        with translation.override('en'):
            response = view.dispatch(u_request)

        assert response.status_code == 302
        assert hasattr(view, 'parent_dispatch_called') is False

        message = list(get_messages(u_request))[0]
        assert message.message == 'You can\'t place orders with empty cart'


class TestPlaceOrderView:

    def test_get_method_returns_form_with_instances_for_user(self, u_request):
        """
        Test that if user is authenticated get method of PlaceOrderView will
        pass forms with user and address instance.
        """
        view = PlaceOrderView(request=u_request)

        response = view.get(u_request)

        forms = response.context_data['forms']
        assert forms['user'].instance == u_request.user
        assert forms['address'].instance == u_request.user.address

    def test_get_method_returns_empty_form(self, a_request):
        """
        Test that if user is anonymous get method of PlaceOrderView will
        pass empty forms.
        """
        view = PlaceOrderView(request=a_request)

        response = view.get(a_request)

        forms = response.context_data['forms']
        assert forms['user'].is_valid() is False
        assert forms['user'].errors == {}
        assert forms['address'].is_valid() is False
        assert forms['address'].errors == {}

    def test_post_method_returns_form_with_errors(self, a_request, form_data):
        """Test that post request will return form with errors if forms
        is invalid.
        """
        # Post code in form_data is not valid.
        data = {**form_data['user'], **form_data['address']}

        # Immutable QueryDict to mutable.
        a_request.POST = a_request.POST.copy()
        a_request.POST.update(data)

        view = PlaceOrderView(request=a_request)

        response = view.post(a_request)

        forms = response.context_data['forms']

        assert forms['user'].is_valid() is True
        assert forms['address'].is_valid() is False
        assert forms['address'].errors.get('postcode') is not None

    def test_post_method_write_data_to_session(self, a_request, form_data):
        """
        Test that if forms are valid form data would be written to user
        session and redirect occure.
        """
        # Change post code to valid postcode
        form_data['address']['postcode'] = '654321'

        data = {**form_data['user'], **form_data['address']}

        # Immutable QueryDict to mutable.
        a_request.POST = a_request.POST.copy()
        a_request.POST.update(data)

        view = PlaceOrderView(request=a_request)

        response = view.post(a_request)

        assert response.status_code == 302
        assert a_request.session.get('form') is not None
        assert a_request.session.get('form') == form_data

    # Functional tests for view. Using Django Client.

    def test_redirects_with_empy_cart(self, client, admin_user):
        response = client.get(reverse('orders:place-order'))
        assert response.status_code == 302
        client.force_login(admin_user)
        response = client.get(reverse('orders:place-order'))
        assert response.status_code == 302

    def test_authenticated_get_request(self, client, user_w_cart):
        """
        Returns template with forms that have user and user address instances
        as initials.
        """
        client.force_login(user_w_cart)

        response = client.get(reverse('orders:place-order'))

        assert response.status_code == 200

        forms = response.context['forms']
        assert forms['user'].instance == user_w_cart
        assert forms['address'].instance == user_w_cart.address

    def test_unauthenticated_get_request(self, client, cart_w_items):
        """
        Returns empty forms for unauthenticated user.
        """
        session = client.session
        session['cart_id'] = cart_w_items.pk
        session.save()

        response = client.get(reverse('orders:place-order'))

        assert response.status_code == 200

        forms = response.context['forms']
        assert forms['user'].is_valid() is False
        assert forms['user'].errors == {}
        assert forms['address'].is_valid() is False
        assert forms['address'].errors == {}

    def test_post_request_store_data(self, user_w_cart, client, form_data):
        """
        Test that valid data will be written to user session and user will
        be redirected to next page.
        """
        client.force_login(user_w_cart)

        form_data['address']['postcode'] = '654321'
        data = {**form_data['user'], **form_data['address']}

        response = client.post(
            reverse('orders:place-order'),
            data,
            follow=True)

        redirect_url, redirect_status = response.redirect_chain[-1]

        assert response.status_code == 200
        assert redirect_url == reverse('orders:check-order')
        assert redirect_status == 302
        assert client.session.get('form') == form_data

    def test_post_request_return_errors(self, user_w_cart, client, form_data):
        """
        Test that invalid data will not be written to session, form with
        errors will be returned instead.
        """
        client.force_login(user_w_cart)

        data = {**form_data['user'], **form_data['address']}

        response = client.post(
            reverse('orders:place-order'),
            data,
            follow=True)

        assert response.status_code == 200
        assert client.session.get('form') is None
        assert response.context['forms']['address'].is_valid() is False


class TestCheckOrderView:

    def test_dispatch_method_redirects_user(self, u_request):
        """
        Test taht dispatch method will redirect user to previous page if
        user has not form_data stored in his session
        """
        # It seems that Request Factory not setting _messages attribute and
        # test fails with error saying that Messages Framework not installed,
        # fix from SO below.

        u_request._messages = FallbackStorage(u_request)

        view = CheckOrderView(request=u_request)
        with translation.override('en'):
            response = view.dispatch(u_request)

        assert response.status_code == 302

        message = list(get_messages(u_request))[0]
        assert message.message == 'Please fill out form to continue'

    def test_dispatch_method_not_redirects_user(self, u_request, user_w_cart):
        """
        Test that dispatch method will not redirect user to previous page
        if user has form_data stored in his session.
        """
        # u_request.method is 'POST'
        def post(self, *args, **kwargs):
            self.super_called = True

        u_request.user = user_w_cart  # Avoid redirect from next dispatch.

        u_request.session['form'] = 'I am data!'

        view = CheckOrderView(request=u_request)
        # https://docs.python.org/3.6/howto/descriptor.html#functions-and-methods
        view.post = post.__get__(view)

        view.dispatch(u_request)

        assert getattr(view, 'super_called', False) is True

    def test_get_context_data_pass_additional_data(self, cart_w_items):
        view = CheckOrderView()
        view.cart = cart_w_items

        context = view.get_context_data()

        assert all([item in context for item in ('cart', 'total')])
        assert context['cart'] == cart_w_items
        assert context['total'] == 6000

    def test_send_email_calls_task(self, form_data, u_request):
        """
        Test that send_email method will call celery task to send email with
        correct args.
        """

        order = Order.objects.create_order_instance(form_data)
        view = CheckOrderView(request=u_request)

        admin_link = u_request.build_absolute_uri(
            reverse('admin:orders_order_change', args=(order.pk,))
        )
        context = {'order': order.pk,
                   'site_name': 'testserver', 'admin_link': admin_link}
        email_templates = {'user': 'orders/emails/email_for_user.html',
                           'manager': 'orders/emails/email_for_manager.html'}
        msg = "Order placed on 3DShop"

        with translation.override('en'):
            with patch('orders.views.send_order_placed_email.delay') as task:
                view.send_email(order)
                task.assert_called_with(msg, context, email_templates)

    def test_get_method_creates_order(self, u_request, form_data):
        """
        Test that get method will create order instance from form_data and pass
        it to context.
        """

        view = CheckOrderView(
            request=u_request, cart=Cart.objects.create(), form_data=form_data
        )

        response = view.get(u_request)

        assert response.context_data.get('order') is not None

    def test_post_method_creates_order_in_db(self, u_request, form_data,
                                             mailoutbox):
        """
        Test that after successfull post request order will be created in
        database.
        """
        # It seems that Request Factory not setting _messages attribute and
        # test fails with error saying that Messages Framework not installed,
        # fix from SO below.
        u_request._messages = FallbackStorage(u_request)

        view = CheckOrderView(
            request=u_request, cart=Cart.objects.create(), form_data=form_data
        )

        with translation.override('en'):
            response = view.post(u_request)

        assert response.status_code == 302
        assert Order.objects.count() == 1

        message = list(get_messages(u_request))[0]
        assert message.message == (
            'Your order now proccessing! Information will be sent to email.')

        assert u_request.session.get('form') is None
        assert len(mailoutbox) == 2

    # Functional tests for view. Using Django Client.

    def test_get_request_returns_order_information(self, user_client):
        """
        Test that on GET request server will return information about
        user order.
        """

        response = user_client.get(reverse('orders:check-order'))

        assert response.status_code == 200
        assert response.context.get('order') is not None

    def test_post_request_creates_new_order_in_db(self, user_client):
        """"
        Test that on POST request new order object will be created and
        saved to database.
        """
        with translation.override('en'):
            response = user_client.post(
                reverse('orders:check-order'),
                {},
                follow=True)

        redirect_url, redirect_status = response.redirect_chain[-1]
        msg = 'Your order now proccessing! Information will be sent to email.'
        assert response.status_code == 200
        assert redirect_url == reverse('onlineshop:home')
        assert redirect_status == 302
        assert Order.objects.count() == 1
        assert msg in response.content.decode('utf-8')