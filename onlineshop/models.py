import os
import uuid
from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from mptt.models import MPTTModel, TreeForeignKey


class Category(MPTTModel):
    parent = TreeForeignKey('Category',
                            on_delete=models.CASCADE,
                            verbose_name=_('Parent'),
                            related_name='children',
                            blank=True,
                            null=True)
    title = models.CharField(_('Title'), max_length=64, unique=True)
    slug = models.SlugField(max_length=50)

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ('title',)

    def get_all_products(self):
        categories = self.get_descendants(
            include_self=True).values_list('id', flat=True)
        return Product.objects.filter(category_id__in=categories)

    def get_absolute_url(self):
        return reverse('onlineshop:category-detail',
                       kwargs={'slug': self.slug})

    def __str__(self):
        return self.title


def default_category():
    return Category.objects.get_or_create(title='Unassigned')[0]


def image_upload_path(instance, name):
    ext = os.path.splitext(name)[1]
    new_name = str(uuid.uuid4())
    return '{}/{}/{}{}'.format(new_name[:2], new_name[2:4], new_name[4:], ext)


class Product(models.Model):

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_DEFAULT,
        verbose_name=_('Category'),
        related_name='products',
        default=default_category
    )

    title = models.CharField(_('Title'), max_length=64)
    slug = models.SlugField(max_length=50)
    price = models.DecimalField(_('Price'),
                                max_digits=9, decimal_places=2,
                                validators=(
                                    MinValueValidator(Decimal('0.01')),
                                ))
    discount = models.IntegerField(_('Discount in %'),
                                   validators=(MaxValueValidator(99),),
                                   default=0
                                   )
    desc = models.TextField(_('Description'),
                            null=True, blank=True)
    date_added = models.DateField(_('Upload Date'), auto_now_add=True)
    stock = models.PositiveIntegerField(_('Stock'))
    image = models.ImageField(_('Image'),
                              upload_to=image_upload_path)
    properties = models.ManyToManyField('Attribute',
                                        through='ProductAttributeValue')

    def get_price(self):
        return Decimal(self.price - self.price * self.discount / 100)

    get_price.short_description = _('Final Price')

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ('title',)

    def in_stock(self):
        return self.stock

    def _in_stock_admin(self):
        return self.in_stock() > 0

    _in_stock_admin.boolean = True
    _in_stock_admin.admin_order_field = 'stock'
    _in_stock_admin.short_description = _('In stock')

    def get_absolute_url(self):
        return reverse('onlineshop:product-detail', kwargs={'slug': self.slug})

    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url

    def __str__(self):
        return self.title


class Attribute(models.Model):
    name = models.CharField(_('Product Attribute'), max_length=64)

    class Meta:
        verbose_name = _('Attribute')
        verbose_name_plural = _('Attributes')

    def __str__(self):
        return self.name


class ProductAttributeValue(models.Model):
    product = models.ForeignKey(Product, verbose_name=_('Product'),
                                on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute,
                                  verbose_name=_('Product Attribute'),
                                  on_delete=models.CASCADE)
    value = models.CharField(max_length=512, null=True, blank=True)

    class Meta:
        verbose_name = _('Product Attribute')
        verbose_name_plural = _('Extra Product\'s Attributes')