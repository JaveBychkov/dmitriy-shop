import json

import pytest
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse

from shoppingcart.models import Cart, Line
from shoppingcart.views import (AddProductView, BaseEditCartView,
                                CartDetailView, CartMixin, ChangeQuantityView,
                                GetJsonDataMixin, RemoveProductView,
                                PriceChangedView)

from .models import ProductModel

pytestmark = pytest.mark.django_db


@pytest.fixture
def product():
    return ProductModel.objects.create(
        price=1000, discount=0, slug='some-some'
    )


@pytest.fixture
def form():
    class Form:

        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def is_valid(self):
            return self.isvalid

    return Form


@pytest.fixture
def valid_form(form):
    form.isvalid = True
    return form


@pytest.fixture
def invalid_form(form):
    form.isvalid = False
    form.errors = {'some_error': 'some_desc'}
    return form


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
def base_cartview():
    return BaseEditCartView()


@pytest.fixture
def valid_cartview(u_request, valid_form, base_cartview):
    base_cartview.request = u_request
    base_cartview.form_class = valid_form
    return base_cartview


@pytest.fixture
def invalid_cartview(u_request, invalid_form, base_cartview):
    base_cartview.request = u_request
    base_cartview.form_class = invalid_form
    return base_cartview


class TestGetAjaxDataMixin:

    class DummyView(GetJsonDataMixin):

        def dummy_form(self, data):
            return data

        form_class = dummy_form

    def test_get_form_data_gather_data_from_request(self, rf):
        view = self.DummyView()
        view.request = rf.post(
            '/', json.dumps({'id_': '2'}), content_type='application/json'
        )
        data = view.get_form_data()
        assert data == {'data': {'id_': '2'}}

    def test_get_form_returns_form_class_with_gathered_data(self, rf):

        view = self.DummyView()
        view.request = rf.post(
            '/', json.dumps({'id_': '2'}), content_type='application/json'
        )
        data = view.get_form()

        assert data == {'id_': '2'}


class TestCartMixin:

    def test_returns_cart_by_id_in_session(self, a_request):
        cart = Cart.objects.create()
        a_request.session['cart_id'] = cart.pk
        mixin = CartMixin()
        mixin.request = a_request

        assert cart == mixin.get_session_cart()

    def test_returns_new_cart_if_no_id_in_session(self, a_request):
        """
        Test that get_session_cart_method will return new cart if
        there is no cart_id in session, and test that it will also
        set cart_id to returned cart
        """
        mixin = CartMixin()
        mixin.request = a_request
        cart = mixin.get_session_cart()

        assert isinstance(cart, Cart)
        assert mixin.request.session.get('cart_id') == cart.pk

    def test_get_cart_returns_cart_for_user(self, u_request):

        mixin = CartMixin()

        cart = Cart.objects.create(owner=u_request.user)
        mixin.request = u_request

        assert cart == mixin.get_cart()

    def test_get_cart_return_new_cart_for_user(self, u_request):
        mixin = CartMixin()
        user = u_request.user

        mixin.request = u_request

        cart = mixin.get_cart()

        assert isinstance(cart, Cart)
        assert user.cart == cart

    def test_get_session_cart_if_user_not_authenticated(self, a_request):
        def get_session_cart(self):
            self.called = True

        mixin = CartMixin()
        mixin.request = a_request
        # https://docs.python.org/3.6/howto/descriptor.html#functions-and-methods
        mixin.get_session_cart = get_session_cart.__get__(mixin)

        mixin.get_cart()

        assert mixin.called


class TestBaseEditCartView:

    def test_adds_user_cart_to_form_data(self, valid_cartview):

        data = valid_cartview.get_form_data()

        assert 'cart' in data

    def test_render_to_response_returns_JsonResponse(self, base_cartview):

        response = base_cartview.render_to_response(message='Test')

        assert response.status_code == 200
        assert json.loads(response.content) == {'message': 'Test'}

        response = base_cartview.render_to_response(message='Test', status=400)
        assert response.status_code == 400

    def test_form_valid(self, valid_cartview):
        response = valid_cartview.form_valid('form obj')
        assert response.status_code == 200
        assert json.loads(response.content) == {'message': 'Ok'}

    def test_form_invalid(self, invalid_cartview, invalid_form):
        invalid_form.errors = {}
        response = invalid_cartview.form_invalid(invalid_form)
        assert response.status_code == 400
        assert json.loads(response.content) == {'errors': 'Error occured'}

        invalid_form.errors = ({'non_field_errors': ['something']})

        response = invalid_cartview.form_invalid(invalid_form)
        assert response.status_code == 400
        assert json.loads(response.content) == {'errors':
                                                {'non_field_errors':
                                                 ['something']}}

    def test_post_return_form_valid(self, u_request, valid_cartview):
        """
        Test that post request handler will return appropriate method
        if form is valid.
        """
        valid_cartview.request = u_request

        response = valid_cartview.post(u_request)

        assert response.status_code == 200

    def test_post_return_form_invalid(self, u_request, invalid_cartview):
        """
        Test that post request handler will return appropriate method if form
        is invalid.
        """
        invalid_cartview.request = u_request

        response = invalid_cartview.post(u_request)

        assert response.status_code == 400


class TestAddProductView:

    def test_form_valid_returns_bad_request_status_code(self):
        view = AddProductView()
        response = view.form_valid('some_form')

        assert response.status_code == 400

    def test_return_badrequest_if_product_does_not_exists(self, form):
        form.errors = {}
        form.cleaned_data = {'id_': 23, 'slug': 'some-some'}
        view = AddProductView()

        response = view.form_invalid(form)

        assert response.status_code == 400

    def test_adds_product_to_cart(self, product, form):
        cart = Cart.objects.create()
        form.cleaned_data = {'id_': product.pk, 'slug': product.slug}
        view = AddProductView()
        view.cart = cart

        response = view.form_invalid(form)

        assert response.status_code == 200
        assert cart.line_set.filter(product=product).exists()

    def test_dont_add_product_to_cart_if_not_in_stock(self, product, form,):
        cart = Cart.objects.create()
        product.stock = 0
        product.save()
        form.cleaned_data = {'id_': product.pk, 'slug': product.slug}
        view = AddProductView()
        view.cart = cart

        response = view.form_invalid(form)

        assert response.status_code == 400
        assert not cart.line_set.filter(product=product).exists()

    # Functional tests for view. Using Django Client.

    def test_c_adds_product(self, client, product):
        """
        Using Django Test client test that product will be added
        to user shopping if everything is ok.
        """
        response = client.post(
            reverse('shoppingcart:add-product'),
            json.dumps({'id_': product.pk, 'slug': product.slug}),
            content_type='application/json'
        )

        assert response.status_code == 200
        assert product.line_set.all().exists()

    def test_c_dont_adds_product_if_not_in_stock(self, client, product):
        """
        Using Django Test client test that product will not be added
        to user shopping cart if product not in stock.
        """
        product.stock = 0
        product.save()

        response = client.post(
            reverse('shoppingcart:add-product'),
            json.dumps({'id_': product.pk, 'slug': product.slug}),
            content_type='application/json'
        )

        assert response.status_code == 400
        assert not product.line_set.all().exists()

    def test_c_dont_adds_if_already_in_cart(self, client, product, admin_user):
        """
        Using Django Test client test that product will not be added
        to user shopping cart if product already in user's cart.
        """
        cart = Cart.objects.create(owner=admin_user)
        Line.objects.create(cart=cart, product=product)

        client.force_login(admin_user)

        response = client.post(
            reverse('shoppingcart:add-product'),
            json.dumps({'id_': product.pk, 'slug': product.slug}),
            content_type='application/json'
        )

        assert response.status_code == 400
        assert product.line_set.all().exists()

    def test_c_dont_adds_if_product_does_not_exists(self, client):
        response = client.post(
            reverse('shoppingcart:add-product'),
            json.dumps({'id_': 18, 'slug': 'hey-hey'}),
            content_type='application/json'
        )

        assert response.status_code == 400


class TestRemoveProductView:

    def test_form_valid_removes_product_from_cart(self, form, product):
        cart = Cart.objects.create()
        Line.objects.create(cart=cart, product=product)

        form.cleaned_data = {'id_': product.pk, 'slug': product.slug}

        view = RemoveProductView()
        view.cart = cart

        response = view.form_valid(form)

        assert response.status_code == 200
        assert not cart.line_set.all().exists()

    # Functional tests for view. Using Django Client.

    def test_c_removes_product_from_cart(self, client, product, admin_user):
        cart = Cart.objects.create(owner=admin_user)
        Line.objects.create(cart=cart, product=product)

        client.force_login(admin_user)

        response = client.post(
            reverse('shoppingcart:remove-product'),
            json.dumps({'id_': product.pk, 'slug': product.slug}),
            content_type='application/json'
        )

        assert response.status_code == 200
        assert not cart.line_set.all().exists()

    def test_c_return_badrequest_if_product_not_in_cart(self, client):
        response = client.post(
            reverse('shoppingcart:remove-product'),
            json.dumps({'id_': 23, 'slug': 'something'}),
            content_type='application/json'
        )

        assert response.status_code == 400


class TestChangeQuantityView:

    def test_form_valid_changes_quantity(self, form, product, admin_user):
        cart = Cart.objects.create(owner=admin_user)
        Line.objects.create(cart=cart, product=product)
        form.cleaned_data = {
            'id_': product.pk, 'slug': product.slug, 'quantity': 20}

        view = ChangeQuantityView()
        view.cart = cart

        response = view.form_valid(form)

        assert response.status_code == 200
        assert Line.objects.filter(quantity=20).exists()

    # Functional tests for view. Using Django Client.

    def test_c_changes_product_quantity(self, client, admin_user, product):
        cart = Cart.objects.create(owner=admin_user)
        Line.objects.create(cart=cart, product=product)

        client.force_login(admin_user)

        response = client.post(
            reverse('shoppingcart:update-quantity'),
            json.dumps(
                {'id_': product.pk, 'slug': product.slug, 'quantity': 10}
            ),
            content_type='application/json'
        )

        assert response.status_code == 200
        assert Line.objects.filter(quantity=10).exists()

    def test_c_returns_badrequest_if_product_not_in_cart(self, client):
        response = client.post(
            reverse('shoppingcart:update-quantity'),
            json.dumps(
                {'id_': 15, 'slug': 'hey-hey', 'quantity': 10}
            ),
            content_type='application/json'
        )

        assert response.status_code == 400
        assert not Line.objects.filter(quantity=10)


class TestPriceChangedView:

    def test_form_valid_set_price_changed_to_false(self, product):
        cart = Cart.objects.create()
        Line.objects.create(cart=cart, product=product, price_changed=True)

        view = PriceChangedView()
        view.cart = cart

        response = view.form_valid('form')

        assert response.status_code == 200
        assert cart.line_set.filter(price_changed=False).exists()

    # Functional tests for view. Using Django Client.

    def test_c_set_price_changed_to_false(self, client, product, admin_user):
        cart = Cart.objects.create(owner=admin_user)
        Line.objects.create(cart=cart, product=product, price_changed=True)

        client.force_login(admin_user)

        response = client.post(
            reverse('shoppingcart:price-changed'),
            json.dumps({'confirm': True}),
            content_type='application/json'
        )

        assert response.status_code == 200
        assert cart.line_set.filter(price_changed=False).exists()


class TestCartDetailView:

    def test_get_context_data_gather_additional_context(self, product):
        cart = Cart.objects.create()
        Line.objects.create(cart=cart, product=product)

        view = CartDetailView()
        view.object = cart

        context = view.get_context_data()

        assert 'total' in context
        assert 'price_changed' in context
        assert context['total'] == 1000
        assert not context['price_changed']

    def test_get_object_return_existing_cart_for_user(self, u_request):
        cart = Cart.objects.create(owner=u_request.user)

        view = CartDetailView()
        view.request = u_request

        assert cart == view.get_object()

    def test_creates_new_cart_for_user(self, u_request):

        view = CartDetailView()
        view.request = u_request
        cart = view.get_object()

        assert u_request.user.cart == cart

    def test_get_cart_from_id_in_session(self, a_request):
        cart = Cart.objects.create()
        a_request.session['cart_id'] = cart.pk
        view = CartDetailView()
        view.request = a_request

        assert cart == view.get_object()

    def test_creates_new_cart_and_write_id_to_session(self, a_request):
        view = CartDetailView()
        view.request = a_request

        cart = view.get_object()

        assert a_request.session.get('cart_id') == cart.pk

    # Functional tests for view. Using Django Client.

    def test_c_get_with_empty_cart(self, client):
        response = client.get(
            reverse('shoppingcart:cart-detail')
        )

        assert response.status_code == 200
        assert response.context['total'] == 0
        assert not response.context['price_changed']
        assert 'no items in your cart' in response.content.decode('utf-8')

    def test_c_get_with_items_in_cart(self, client, product, admin_user):
        cart = Cart.objects.create(owner=admin_user)
        Line.objects.create(cart=cart, product=product)

        client.force_login(admin_user)

        response = client.get(
            reverse('shoppingcart:cart-detail')
        )

        assert response.status_code == 200
        assert response.context['total'] == 1000
        assert not response.context['price_changed']
        assert 'no items in your cart' not in response.content.decode('utf-8')

    def test_c_get_with_price_changed_lines(self, client, product, admin_user):
        cart = Cart.objects.create(owner=admin_user)
        Line.objects.create(cart=cart, product=product, price_changed=True)

        client.force_login(admin_user)

        response = client.get(
            reverse('shoppingcart:cart-detail')
        )
        msg = 'products in your shopping cart has changed in price'
        assert response.status_code == 200
        assert response.context['total'] == 1000
        assert response.context['price_changed']
        assert 'no items in your cart' not in response.content.decode('utf-8')
        assert msg in response.content.decode('utf-8')

    def test_c_get_with_cart_in_session(self, client):
        cart = Cart.objects.create()
        session = client.session
        session['cart_id'] = cart.pk
        session.save()

        response = client.get(
            reverse('shoppingcart:cart-detail')
        )

        assert response.status_code == 200
        assert response.context['total'] == 0
        assert not response.context['price_changed']
        assert 'no items in your cart' in response.content.decode('utf-8')
