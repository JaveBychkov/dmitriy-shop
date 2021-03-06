from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _
from .models import User, Address


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def clean_email(self):
        # TODO: Find a better way to make email unique.
        # unique_together ?
        email = self.cleaned_data['email']
        initial_email = self.initial.get('email')
        if initial_email == email:
            return email
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                _('User with given email already exists'), code='invalid')
        return email


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

    def clean_email(self):
        email = self.cleaned_data['email']
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                _('User with given email already exists'), code='invalid')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
