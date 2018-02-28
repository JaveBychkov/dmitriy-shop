from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.html import escape

from .tasks import send_feedback


class FeedbackForm(forms.Form):

    name = forms.CharField(max_length=128, label=_('Your name'))
    email = forms.EmailField(max_length=128, label=_('Email'))
    message = forms.CharField(widget=forms.Textarea, label=_('Your message'))

    def send_feedback_email(self):
        data = self.get_sanitazied_data()
        send_feedback.delay(data)

    def get_sanitazied_data(self):
        """Returns escaped data."""
        return {k: escape(v) for k, v in self.cleaned_data.items()}
