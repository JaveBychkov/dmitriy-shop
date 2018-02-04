from django import forms
from django.utils.translation import ugettext_lazy as _


class BaseForm(forms.Form):
    """
    Base form for other forms in project.

    Additionally sets self.cart attribute on form instance.
    """

    def __init__(self, *args, **kwargs):
        self.cart = kwargs.pop('cart')
        super().__init__(*args, **kwargs)


class ProductForm(BaseForm):
    """
    Product form.

    Excepts product id and product slug as it's data.
    """

    id_ = forms.IntegerField(min_value=0)
    slug = forms.SlugField()

    def clean(self):
        """Validate that product with given id and slug exists in user cart."""
        cleaned_data = super().clean()
        id_, slug = cleaned_data.get('id_'), cleaned_data.get('slug')

        product_in_cart = self.cart.line_set.filter(
            product__id=id_, product__slug=slug
        ).exists()

        if product_in_cart:
            return cleaned_data
        else:
            self.add_error(
                None, forms.ValidationError(_('Product not in cart'))
            )


class ProductQuantityForm(ProductForm):
    """Form used in view that handles product quantity changes."""

    quantity = forms.IntegerField(min_value=0)


class PriceChangedForm(BaseForm):
    """Form used in view that handles price changes."""

    confirm = forms.BooleanField()
