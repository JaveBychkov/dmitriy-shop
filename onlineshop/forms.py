from django import forms


class AddDiscountForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    discount = forms.IntegerField(max_value=99, min_value=0)