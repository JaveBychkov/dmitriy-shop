import json

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Prefetch
from django.http import JsonResponse
from django.utils.translation import ugettext as _
from django.views import View, generic

from .forms import PriceChangedForm, ProductForm, ProductQuantityForm
from .models import Cart, Line


try:
    Product = apps.get_model(settings.PRODUCT_MODEL)
except LookupError:
    raise ImproperlyConfigured('Define PRODUCT_MODEL in settings')
except ValueError:
    raise ImproperlyConfigured(
        'PRODUCT_MODEL should be in the following format: "MyApp.ModelName"'
    )


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


class CartMixin:
    """
    Mixin that provides methods to get cart object for user.

    If user is authenticated he either get his already existed cart or new cart
    will be created and associated with user.

    If user is not authenticated get_session_cart will try to get cart id from
    user session and if this id exists will return user's cart, otherwise new
    cart will be created and this cart id will be stored in user's session so 
    he can access same cart on his next visit.
    """

    def get_cart(self):
        if self.request.user.is_authenticated:
            return Cart.objects.get_or_create(owner=self.request.user)[0]
        else:
            return self.get_session_cart()

    def get_session_cart(self):
        cart_id = self.request.session.get('cart_id')
        # We can filter qs using None and catch DoesNotExist but it's
        # less explicit than checking if it's None.
        if cart_id is None:
            cart = Cart.objects.create()
            self.request.session['cart_id'] = cart.id
            return cart
        return Cart.objects.get(pk=cart_id)


class BaseEditCartView(GetJsonDataMixin, CartMixin, View):
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
        self.cart = self.get_cart()
        data.update({'cart': self.get_cart()})
        return data


class AddProductView(BaseEditCartView):
    """View that handles requests for adding products to shoppingcart

    Expects Ajax request with data in following format:

    {"id_": 12, "slug": "some-slug"}

    Where:
        id_ : int
            Product id.
        slug : str
            Product slug.
    """

    form_class = ProductForm

    def form_valid(self, form):
        """
        Returns Bad Request response.

        Because our form .clean() method checks whether product presists in
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
        id_, slug = form.cleaned_data['id_'], form.cleaned_data['slug']
        try:
            product = Product.objects.get(id=id_, slug=slug)
        except Product.DoesNotExist:
            return super().form_invalid(form)

        if not product.in_stock():
            return self.render_to_response(
                message=_('Product not in stock'), status=400
            )

        cart_line = Line.objects.create(product=product, cart=self.cart)
        self.cart.line_set.add(cart_line)

        return self.render_to_response(
            message=_('Product successfuly added to cart!')
        )


class RemoveProductView(BaseEditCartView):

    """View that handles requests for removing products from user's cart

    Expects Ajax request with data in following format:

    {"id_": 12, "slug": "some-slug"}

    Where:
        id_ : int
            Product id.
        slug : str
            Product slug.
    """

    form_class = ProductForm

    def form_valid(self, form):
        """Removes product from user's cart."""
        id_, slug = form.cleaned_data['id_'], form.cleaned_data['slug']

        self.cart.line_set.filter(product__id=id_, product__slug=slug).delete()

        return self.render_to_response(
            message=_('Successfully removed')
        )


class ChangeQuantityView(BaseEditCartView):

    """View that handles requests for changing quantity of product in cart

    Expects Ajax request with data in following format:

    {"id_": 12, "slug": "some-slug", "quantity": "2"}

    Where:
        id_ : int
            Product id.
        slug : str
            Product slug.
        quantity : int
            New quantity of product.
    """

    form_class = ProductQuantityForm

    def form_valid(self, form):
        """Changes product's quantity."""
        id_, slug = form.cleaned_data['id_'], form.cleaned_data['slug']

        line = self.cart.line_set.filter(product__id=id_, product__slug=slug)
        line = line.get()

        line.quantity = form.cleaned_data['quantity']
        line.save()

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

    model = Cart
    prefetch = Prefetch(
        'line_set', queryset=Line.objects.select_related('product')
    )
    queryset = Cart.objects.prefetch_related(prefetch)

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

        line_set = self.object.line_set.all()
        prices = [line.total_price() for line in line_set]

        context['total'] = sum(prices)
        context['price_changed'] = any([x.price_changed for x in line_set])
        return context

    def get_object(self):
        """
        Get cart object for user either associated with registered user or one
        from session for unregistered users.
        """
        if self.request.user.is_authenticated:
            try:
                obj = self.queryset.filter(owner=self.request.user).get()
            except Cart.DoesNotExist:
                obj = Cart.objects.create(owner=self.request.user)
        else:
            cart_id = self.request.session.get('cart_id')
            # We can filter qs using None and catch DoesNotExist but it's
            # less explicit than checking if it's None.
            if cart_id is not None:
                obj = self.queryset.filter(pk=cart_id).get()
            else:
                obj = Cart.objects.create()
                self.request.session['cart_id'] = obj.pk

        return obj
