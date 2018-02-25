from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Reminder(models.Model):
    product = models.ForeignKey(settings.PRODUCT_MODEL,
                                verbose_name=_('Product'),
                                on_delete=models.CASCADE)
    email = models.EmailField(_('Email'))

    class Meta:
        unique_together = (('product', 'email'),)