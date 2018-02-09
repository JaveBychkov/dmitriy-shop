from django.db import models


class ProductModel(models.Model):
    slug = models.SlugField()
    price = models.DecimalField(decimal_places=2, max_digits=9)
    discount = models.PositiveIntegerField()
    stock = models.IntegerField(default=1)

    class Meta:
        app_label = 'tests'

    def get_price(self):
        return self.price

    def in_stock(self):
        return self.stock
