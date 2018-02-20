import json

import pytest
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse

from onlineshop.tests.factories import product_factory

from shoppingcart.models import Cart, Line
from shoppingcart.views import (AddProductView, BaseEditCartView,
                                CartDetailView, ChangeQuantityView,
                                GetJsonDataMixin, RemoveProductView,
                                PriceChangedView)


pytestmark = pytest.mark.django_db


@pytest.fixture
def form_class():
    class Form:

        def __init__(self, cached_product=None, *args, **kwargs):
            self.cached_product = cached_product
            self.args = args
            self.kwargs = kwargs

        def get_product(self):
            return self.cached_product

        def is_valid(self):
            return self.isvalid

    return Form


@pytest.fixture
def form(form_class):
    return form_class()


@pytest.fixture
def valid_form(form_class):
    form_class.isvalid = True
    return form_class


@pytest.fixture
def invalid_form(form_class):
    form_class.isvalid = False
    form_class.errors = {'some_error': 'some_desc'}
    return form_class


@pytest.fixture
def base_cartview():
    return BaseEditCartView


@pytest.fixture
def valid_cartview(u_request, valid_form, base_cartview):
    return base_cartview(request=u_request, form_class=valid_form)


@pytest.fixture
def invalid_cartview(u_request, invalid_form, base_cartview):
    return base_cartview(request=u_request, form_class=invalid_form)


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


class TestBaseEditCartView:

    def test_adds_user_cart_to_form_data(self, valid_cartview):

        data = valid_cartview.get_form_data()

        assert 'cart' in data

    def test_render_to_response_returns_JsonResponse(self, base_cartview):

        response = base_cartview().render_to_response(message='Test')

        assert response.status_code == 200
        assert json.loads(response.content) == {'message': 'Test'}

        response = base_cartview().render_to_response(message='Test', status=400)
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
        form.cleaned_data = {'id_': 23}
        view = AddProductView()

        response = view.form_invalid(form)

        assert response.status_code == 400

    def test_adds_product_to_cart(self, product, form):
        form.cached_product = product
        cart = Cart.objects.create()
        form.cleaned_data = {'id_': product.pk}
        view = AddProductView()
        view.cart = cart

        response = view.form_invalid(form)

        assert response.status_code == 200
        assert cart.line_set.filter(product=product).exists() is True

    def test_dont_add_product_to_cart_if_not_in_stock(self, product, form):
        cart = Cart.objects.create()
        product.stock = 0
        product.save()

        form.cached_product = product
        form.cleaned_data = {'id_': product.pk}

        view = AddProductView()
        view.cart = cart

        response = view.form_invalid(form)

        assert response.status_code == 400
        assert cart.line_set.filter(product=product).exists() is False

    # Functional tests for view. Using Django Client.

    def test_c_adds_product(self, client, product):
        """
        Using Django Test client test that product will be added
        to user shopping if everything is ok.
        """
        response = client.post(
            reverse('shoppingcart:add-product'),
            json.dumps({'id_': product.pk}),
            content_type='application/json'
        )

        assert response.status_code == 200
        assert product.line_set.all().exists() is True

    def test_c_dont_adds_product_if_not_in_stock(self, client, product):
        """
        Using Django Test client test that product will not be added
        to user shopping cart if product not in stock.
        """
        product.stock = 0
        product.save()

        response = client.post(
            reverse('shoppingcart:add-product'),
            json.dumps({'id_': product.pk}),
            content_type='application/json'
        )

        assert response.status_code == 400
        assert product.line_set.all().exists() is False

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
            json.dumps({'id_': product.pk}),
            content_type='application/json'
        )

        assert response.status_code == 400
        assert product.line_set.all().exists() is True

    def test_c_dont_adds_if_product_does_not_exists(self, client):
        response = client.post(
            reverse('shoppingcart:add-product'),
            json.dumps({'id_': 18}),
            content_type='application/json'
        )

        assert response.status_code == 400


class TestRemoveProductView:

    def test_form_valid_removes_product_from_cart(self, form, product):
        cart = Cart.objects.create()
        Line.objects.create(cart=cart, product=product)

        form.cached_product = product
        form.cleaned_data = {'id_': product.pk}

        view = RemoveProductView()
        view.cart = cart

        response = view.form_valid(form)

        assert response.status_code == 200
        assert cart.line_set.all().exists() is False

    # Functional tests for view. Using Django Client.

    def test_c_removes_product_from_cart(self, client, product, admin_user):
        cart = Cart.objects.create(owner=admin_user)
        Line.objects.create(cart=cart, product=product)

        client.force_login(admin_user)

        response = client.post(
            reverse('shoppingcart:remove-product'),
            json.dumps({'id_': product.pk}),
            content_type='application/json'
        )

        assert response.status_code == 200
        assert cart.line_set.all().exists() is False

    def test_c_return_badrequest_if_product_not_in_cart(self, client):
        response = client.post(
            reverse('shoppingcart:remove-product'),
            json.dumps({'id_': 23}),
            content_type='application/json'
        )

        assert response.status_code == 400


class TestChangeQuantityView:

    def test_form_valid_changes_quantity(self, form, product, admin_user):
        cart = Cart.objects.create(owner=admin_user)
        Line.objects.create(cart=cart, product=product)
        
        form.cached_product = product
        form.cleaned_data = {
            'id_': product.pk, 'quantity': 3}

        view = ChangeQuantityView()
        view.cart = cart

        response = view.form_valid(form)

        assert response.status_code == 200
        assert Line.objects.filter(quantity=3).exists() is True

    def test_form_valid_returns_400_status(self, form, product, admin_user):
        """
        Test that form valid method will return Bad Request if requested
        quantity change is greater than available product.
        """
        cart = Cart.objects.create(owner=admin_user)
        Line.objects.create(cart=cart, product=product)

        form.cached_product = product
        form.cleaned_data = {
            'id_': product.pk, 'quantity': 20}

        view = ChangeQuantityView()
        view.cart = cart

        response = view.form_valid(form)

        assert response.status_code == 400
        assert Line.objects.filter(quantity=20).exists() is False

    # Functional tests for view. Using Django Client.

    def test_c_changes_product_quantity(self, client, admin_user, product):
        cart = Cart.objects.create(owner=admin_user)
        Line.objects.create(cart=cart, product=product)

        client.force_login(admin_user)

        response = client.post(
            reverse('shoppingcart:update-quantity'),
            json.dumps(
                {'id_': product.pk, 'quantity': 2}
            ),
            content_type='application/json'
        )

        assert response.status_code == 200
        assert Line.objects.filter(quantity=2).exists() is True

    def test_c_returns_badrequest_if_product_not_in_cart(self, client):
        response = client.post(
            reverse('shoppingcart:update-quantity'),
            json.dumps(
                {'id_': 15, 'quantity': 2}
            ),
            content_type='application/json'
        )

        assert response.status_code == 400


class TestPriceChangedView:

    def test_form_valid_set_price_changed_to_false(self, product):
        cart = Cart.objects.create()
        Line.objects.create(cart=cart, product=product, price_changed=True)

        view = PriceChangedView()
        view.cart = cart

        response = view.form_valid('form')

        assert response.status_code == 200
        assert cart.line_set.filter(price_changed=False).exists() is True

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
        assert cart.line_set.filter(price_changed=False).exists() is True


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
        assert context['price_changed'] is False

    def test_get_object_return_existing_cart_for_user(self, u_request):
        cart = Cart.objects.create(owner=u_request.user)

        view = CartDetailView(request=u_request)

        assert cart == view.get_object()

    def test_creates_new_cart_for_user(self, u_request):

        view = CartDetailView(request=u_request)

        cart = view.get_object()

        assert u_request.user.cart == cart

    def test_get_cart_from_id_in_session(self, a_request):
        cart = Cart.objects.create()
        a_request.session['cart_id'] = cart.pk
        view = CartDetailView(request=a_request)

        assert cart == view.get_object()

    def test_creates_new_cart_and_write_id_to_session(self, a_request):
        view = CartDetailView(request=a_request)

        cart = view.get_object()

        assert a_request.session.get('cart_id') == cart.pk

    # Functional tests for view. Using Django Client.

    def test_c_get_with_empty_cart(self, client):
        response = client.get(
            reverse('shoppingcart:cart-detail')
        )

        assert response.status_code == 200
        assert response.context['total'] == 0
        assert response.context['price_changed'] is False

    def test_c_get_with_items_in_cart(self, client, product, admin_user):
        cart = Cart.objects.create(owner=admin_user)
        Line.objects.create(cart=cart, product=product)

        client.force_login(admin_user)

        response = client.get(
            reverse('shoppingcart:cart-detail')
        )

        assert response.status_code == 200
        assert response.context['total'] == 1000
        assert response.context['price_changed'] is False

    def test_c_get_with_price_changed_lines(self, client, product, admin_user):
        cart = Cart.objects.create(owner=admin_user)
        Line.objects.create(cart=cart, product=product, price_changed=True)

        client.force_login(admin_user)

        response = client.get(
            reverse('shoppingcart:cart-detail')
        )
        assert response.status_code == 200
        assert response.context['total'] == 1000
        assert response.context['price_changed'] is True

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
        assert response.context['price_changed'] is False
