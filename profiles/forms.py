from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _
from .models import User, Address


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class AddressForm(forms.ModelForm):

    class Meta:
        model = Address
        fields = (
            'country', 'city', 'street', 'postcode', 'house', 'apartment'
        )


class UserWEmailCreationForm(UserCreationForm):

    email = forms.EmailField(
        label=_("Email")
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
