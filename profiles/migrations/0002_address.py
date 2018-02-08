# Generated by Django 2.0.1 on 2018-02-06 10:21

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(max_length=128, verbose_name='Country')),
                ('city', models.CharField(max_length=128, verbose_name='City')),
                ('street', models.CharField(max_length=128, verbose_name='Street')),
                ('postcode', models.CharField(max_length=6, validators=[django.core.validators.RegexValidator('^\\d{6,6}$')], verbose_name='Postcode')),
                ('house', models.CharField(max_length=10, verbose_name='House number')),
                ('apartment', models.CharField(max_length=10, verbose_name='Apartment')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
        ),
    ]
