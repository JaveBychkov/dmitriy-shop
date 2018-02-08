from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Cart(models.Model):
    """
    Model that represents user shopping cart.
    """
    owner = models.OneToOneField(settings.AUTH_USER_MODEL,
                                 verbose_name=_('Owner'),
                                 on_delete=models.CASCADE,
                                 null=True,
                                 blank=True)

    def product_in_cart(self, product):
        """Check that passed product exists in cart

        Parameters:
        -----------
        product : models.Model
            Instance of PRODUCT_MODEL defined in settings.PRODUCT_MODEL

        Returns:
        --------
        bool
            True or False
        """
        return self.line_set.filter(product=product).exists()

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
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE,
                             verbose_name=_('Cart'), null=True)
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
