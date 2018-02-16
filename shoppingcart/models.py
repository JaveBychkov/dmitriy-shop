from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from orders.models import Order


class CartManager(models.Manager):

    def get_cart(self, user, session, queryset=None):
        """
        Returns associated with current user shopping cart.

        Parameters:
        -----------
        user : models.Model
            Instance of AUTH_USER_MODEL defined in settings.AUTH_USER_MODEL

        Returns:
        --------
        cart
            Cart object.
        """
        # queryset = queryset or self.get_queryset()
        # Statement above will result in unnecessary query, so we're going to
        # check if queryset is none explicitly.

        if queryset is None:
            queryset = self.get_queryset()

        if user.is_authenticated:
            try:
                return queryset.filter(owner=user).get()
            except self.model.DoesNotExist:
                return self.create(owner=user)
        else:
            return self.get_session_cart(user, session, queryset)

    def get_session_cart(self, user, session, queryset=None):
        """Try to get cart by id stored in user session."""
        if queryset is None:
            queryset = self.get_queryset()

        cart_id = session.get('cart_id')

        if cart_id is None:
            return self.create_session_cart(session)

        # In case when cart with cart_id written to session were deleted just
        # return new cart.

        try:
            return queryset.filter(pk=cart_id).get()
        except self.model.DoesNotExist:
            return self.create_session_cart(session)

    def create_session_cart(self, session):
        """Create cart and write it's id in user session."""
        cart = self.create()
        session['cart_id'] = cart.pk
        return cart

    def get_full_cart(self, user, session):
        """
        Prefetch all resources related to cart like cart's lines, and
        products that belongs to said lines.
        """
        prefetch = models.Prefetch(
            'line_set', queryset=Line.objects.select_related('product')
        )
        qs = Cart.objects.prefetch_related(prefetch)

        return self.get_cart(user, session, qs)


class Cart(models.Model):
    """
    Model that represents user shopping cart.
    """
    owner = models.OneToOneField(settings.AUTH_USER_MODEL,
                                 verbose_name=_('Owner'),
                                 on_delete=models.CASCADE,
                                 null=True,
                                 blank=True)
    objects = CartManager()

    def product_in_cart(self, product):
        """Check that passed product exists in cart

        Parameters:
        -----------
        product : models.Model
            Instance of PRODUCT_MODEL defined in settings.PRODUCT_MODEL

        Returns:
        --------
        bool
            True if product in cart, False otherwise. 
        """
        return self.line_set.filter(product=product).exists()

    def add_product(self, product):
        """
        Creates new line object with given product and associates it with
        current cart.
        """
        Line.objects.create(product=product, cart=self)

    def remove_product(self, product):
        """Removes line objects with given product from cart

        Parameters:
        -----------
        product : models.Model
            Instance of PRODUCT_MODEL defined in settings.PRODUCT_MODEL

        Returns:
        --------
        None
        """
        self.line_set.get(product=product).delete()

    def change_product_quantity(self, product, quantity):
        """Changes product quantity in cart

        Parameters:
        -----------
        product : models.Model
            Instance of PRODUCT_MODEL defined in settings.PRODUCT_MODEL
        quantity: int
            New quantity of product.

        Returns:
        --------
        None
        """
        # Note: save() not called, signals not dispatched
        self.line_set.filter(product=product).update(quantity=quantity)

    def get_total_price(self):
        """Returns total price of all products in cart.

        You should use Cart.objects.get_full_cart(request, session) to reduce
        ammount of queries.

        Returns:
        --------
        decimal
            Total price for a cart.
        """
        return sum([line.total_price() for line in self.line_set.all()])

    def any_product_price_changed(self):
        """Returns bool that shows whether price for products was changed.

        Returns:
        --------
        bool
            True if price changed, False otherwice.
        """
        return any([x.price_changed for x in self.line_set.all()])

    class Meta:
        verbose_name = _('Cart')
        verbose_name_plural = _('Carts')


class Line(models.Model):
    """
    Model that represents position in shopping cart.
    """
    product = models.ForeignKey(settings.PRODUCT_MODEL,
                                verbose_name=_('Product'),
                                on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE,
                             verbose_name=_('Cart'), null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE,
                              verbose_name=_('Order'), null=True,
                              related_name='products')
    final_price = models.DecimalField(_('Final Price'),
                                      max_digits=9, decimal_places=2,
                                      validators=[
                                      MinValueValidator(Decimal('0.01'))],
                                      blank=True, null=True)
    price_changed = models.BooleanField(_('Did the price changed?'),
                                        default=False)
    quantity = models.PositiveIntegerField(_('Quantity'), default=1)

    def total_price(self):
        """Return total price for current position"""
        return self.quantity * self.product.get_price()
