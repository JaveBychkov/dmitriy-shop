# Generated by Django 2.0.1 on 2018-02-17 12:56

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_auto_20180217_1555'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='total',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='Total price for an order'),
        ),
    ]
