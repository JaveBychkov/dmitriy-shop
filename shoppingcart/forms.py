from django import forms
from django.utils.translation import ugettext_lazy as _

from onlineshop.models import Product


class BaseForm(forms.Form):
    """
    Base form for other forms in project.

    The 'cart' parameter is set for validation purposes.
    """

    def __init__(self, cart=None, *args, **kwargs):
        self.cart = cart
        self.cached_product = None
        super().__init__(*args, **kwargs)


class ProductForm(BaseForm):
    """
    Product form.

    Excepts product id as it's data.
    """

    id_ = forms.IntegerField(min_value=0)

    def clean(self):
        cleaned_data = super().clean()
        id_ = cleaned_data.get('id_')
        try:
            self.cached_product = Product.objects.get(pk=id_)
        except Product.DoesNotExist:
            raise forms.ValidationError(_('Invalid data'), code='invalid')

        self.check_product_in_cart()

        return cleaned_data

    def get_product(self):
        return self.cached_product

    def check_product_in_cart(self):
        if not self.cart.line_set.filter(product=self.cached_product).exists():
            raise forms.ValidationError(
                _('Product not in cart'), code='invalid'
            )


class ProductQuantityForm(ProductForm):
    """Form used in view that handles product quantity changes."""

    quantity = forms.IntegerField(min_value=0)


class PriceChangedForm(BaseForm):
    """Form used in view that handles price changes."""

    confirm = forms.BooleanField()
