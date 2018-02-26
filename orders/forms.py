from django import forms
from django.utils.translation import ugettext_lazy as _

from profiles.models import User


class UserForm(forms.ModelForm):

    # Redefine fields to make them required
    last_name = forms.CharField(max_length=64, label=_('Last Name'))
    first_name = forms.CharField(max_length=64, label=_('First Name'))
    email = forms.EmailField(max_length=64, label=_('Email'))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
