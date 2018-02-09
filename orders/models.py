from django.db import models
from django.conf import settings

from shoppingcart.models import Line


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    product = s