from decimal import Decimal

from django.core.validators import MinValueValidator
from django.conf import settings
from django.db import models, transaction
from django.utils.translation import ugettext, ugettext_lazy as _


class OrderManager(models.Manager):

    def create_order_instance(self, form_data):
        user_data = form_data['user']
        address_data = form_data['address']

        address = ugettext("{country}, {city}, {street}, {postcode}, "
                           "h.{house}, ap.{apartment}").format(**address_data)

        order_data = {
            'email': '{email}'.format(**user_data),
            'full_name': '{first_name} {last_name}'.format(**user_data),
            'address': address
        }
        return Order(**order_data)


class Order(models.Model):
    PROCESS = 'P'
    ACCEPTED = 'A'
    SENT = 'S'
    CLOSED = 'C'
    STATUSES = (
        (PROCESS, _('In process')),
        (ACCEPTED, _('Accepted')),
        (SENT, _('Sent')),
        (CLOSED, _('Closed')),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('User'), blank=True, null=True)
    email = models.EmailField(
        _('Customer Email'), db_index=True, default='')
    full_name = models.CharField(
        _('Customer Full Name'), max_length=256, default='')
    address = models.CharField(_('Address'), max_length=512, default='')
    date = models.DateTimeField(_('Date of creation'), auto_now_add=True)
    status = models.CharField(_('Status'),
                              max_length=1, choices=STATUSES, default=PROCESS)
    total = models.DecimalField(_('Total price for an order'),
                                max_digits=9, decimal_places=2,
                                validators=(
                                    MinValueValidator(Decimal('0.01')),
                                ), null=True, blank=True)
    objects = OrderManager()

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    def __str__(self):
        return ugettext('Order# {}').format(self.pk)

    def from_cart_to_order(self, cart):
        """Method that helps to finish order model: get total and products
        from cart and, if exists, user.

        Parameters:
        -----------
        cart
            Cart object.
        Returns:
        --------
        None
        """
        self.total = cart.get_total_price()
        # If cart has owner it means that user is authenticated and we want to
        # associate this order with user so we can show it in user's order
        # history.
        self.user = getattr(cart, 'owner', None)
        # Call save first before setting related objects to unsaved order
        # instance.
        self.save()
        self.products.set(cart.line_set.all(), clear=True)
        with transaction.atomic():
            for line in self.products.all():
                product = line.product
                product.stock = models.F('stock') - line.quantity
                line.final_price = line.total_price()
                product.save()
                line.save()
        cart.line_set.clear()
