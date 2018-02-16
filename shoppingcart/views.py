import json

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Prefetch
from django.http import JsonResponse
from django.utils.translation import ugettext as _
from django.views import View, generic

from onlineshop.models import Product

from .forms import PriceChangedForm, ProductForm, ProductQuantityForm
from .models import Cart, Line


class GetJsonDataMixin:
    """
    Mixin that provides methods to get form instance with json request data as
    form data.
    """

    def get_form(self):
        return self.form_class(**self.get_form_data())

    def get_form_data(self):
        data = json.loads(self.request.body.decode('utf-8'))
        return {'data': data}


class BaseEditCartView(GetJsonDataMixin, View):
    """
    Base view that define default methods for all views that edit cart.
    """

    form_class = None

    def post(self, request, *args, **kwargs):
        """Post request handler"""
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        """Valid Form Handler"""
        return self.render_to_response(message=_('Ok'))

    def form_invalid(self, form):
        """Invalid Form Handler"""
        message = form.errors or 'Error occured'
        return self.render_to_response(errors=message, status=400)

    def render_to_response(self, status=200, **kwargs):
        """
        Returns JsonResponse with passed kwargs as data and status as
        HTTP status_code.
        """
        return JsonResponse(kwargs, status=status)

    def get_form_data(self):
        """
        Overriding method from GetJsonDataMixin so our form will get
        one additional keyword argument - user's shopping cart.
        Also instance of view will get .cart attribute that contains current
        user cart.
        """
        data = super().get_form_data()

        user_and_session = self.request.user, self.request.session
        self.cart = Cart.objects.get_cart(*user_and_session)

        data.update({'cart': self.cart})
        return data


class AddProductView(BaseEditCartView):
    """
    View that handles requests for adding products to shoppingcart

    Expects Ajax request with data in following format:

    {"id_": 12}

    Where:
        id_ : int
            Product id.
    """

    form_class = ProductForm

    def form_valid(self, form):
        """
        Returns Bad Request response.

        Because our form .clean() method checks whether product is in
        cart - valid form means that product already in cart and should'nt
        be added once again.
        """
        return self.render_to_response(
            message=_('Product already in your cart'), status=400
        )

    def form_invalid(self, form):
        """
        Adds product to user's cart.

        Form invalid means that product not in user's cart and it can be added.

        Envisages possibilities such as user knowingly sends wrong id and slug
        or product not in stock.
        In both cases such requests results in Bad Request response.
        """

        # We need explicitly check for product to be None because of how our
        # product form works
        product = form.get_product()
        if product is None:
            return super().form_invalid(form)

        if not product.in_stock():
            return self.render_to_response(
                message=_('Product not in stock'), status=400
            )

        self.cart.add_product(product)

        return self.render_to_response(
            message=_('Product successfuly added to cart!')
        )


class RemoveProductView(BaseEditCartView):
    """
    View that handles requests for removing products from user's cart

    Expects Ajax request with data in following format:

    {"id_": 12}

    Where:
        id_ : int
            Product id.
    """

    form_class = ProductForm

    def form_valid(self, form):
        """Removes product from user's cart."""
        product = form.get_product()

        self.cart.remove_product(product)

        return self.render_to_response(
            message=_('Successfully removed')
        )


class ChangeQuantityView(BaseEditCartView):
    """
    View that handles requests for changing quantity of product in cart

    Expects Ajax request with data in following format:

    {"id_": 12, "quantity": "2"}

    Where:
        id_ : int
            Product id.
        quantity : int
            New quantity of product.
    """

    form_class = ProductQuantityForm

    def form_valid(self, form):
        """Changes product's quantity."""
        product = form.get_product()
        quantity = form.cleaned_data['quantity']

        if product.in_stock() < quantity:
            return self.render_to_response(
                message=_('Product not in stock'), status=400
            )

        self.cart.change_product_quantity(product, quantity)

        return self.render_to_response(message=_('ok'))


class PriceChangedView(BaseEditCartView):

    """
    View that handles requests with user confirmation about seeing
    warning message that says that one or more products in user's cart has
    changed price.

    Expects Ajax request with data in following format:

    {"confirm": true}

    Where `confirm` should be true or notification will not be removed from
    cart's detail page.
    """

    form_class = PriceChangedForm

    def form_valid(self, form):
        self.cart.line_set.update(price_changed=False)
        return super().form_valid(form)


class CartDetailView(generic.DetailView):

    model = Cart  # We don't actually need it.

    def get_context_data(self, **kwargs):
        """Gather additional context data.

        Such as:

        total : int
            Purchase amount.

        price_changed : bool
            True or False. If True warning message will be displayed and will
            not if False.
        """
        context = super().get_context_data(**kwargs)

        context['total'] = self.object.get_total_price()
        context['price_changed'] = self.object.any_product_price_changed()
        return context

    def get_object(self):
        """
        Get associated cart object for user.
        """
        user_and_session = self.request.user, self.request.session
        return Cart.objects.get_full_cart(*user_and_session)
