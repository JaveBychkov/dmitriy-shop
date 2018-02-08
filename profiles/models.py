from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _


postcode_validator = RegexValidator(
    r'^\d{6,6}$', message=_('The postal code must consist of 6 digits'))


class Address(models.Model):
    user = models.OneToOneField('User', verbose_name=_('User'),
                                on_delete=models.CASCADE)
    country = models.CharField(_('Country'), max_length=128, null=True)
    city = models.CharField(_('City'), max_length=128, null=True)
    street = models.CharField(_('Street'), max_length=128, null=True)
    postcode = models.CharField(_('Postcode'), max_length=6,
                                validators=[postcode_validator],
                                null=True)
    house = models.CharField(_('House number'), max_length=10, null=True)
    apartment = models.CharField(_('Apartment'), max_length=10, null=True)


class User(AbstractUser):
    pass

    def has_address(self):
        return hasattr(self, 'address')


@receiver(post_save, sender=User)
def create_address(sender, instance, created, **kwargs):
    if created:
        Address.objects.create(user=instance)