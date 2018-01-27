from onlineshop.models import (Product, Category, Attribute,
                               ProductAttributeValue)


def category_factory(to_db=True, **kwargs):
    defaults = {
        'title': 'Clothes',
        'slug': 'clothes',
    }
    defaults.update(kwargs)
    if to_db:
        return Category.objects.get_or_create(**defaults)[0]
    return Category(**defaults)


def product_factory(to_db=True, add_category=True, **kwargs):
    defaults = {
        'title': 'Socks',
        'slug': 'socks',
        'price': 12.99,
        'desc': 'High quality cotton socks',
        'stock': 126,
        'image': '',
        'discount': 0
    }
    defaults.update(kwargs)
    if add_category and 'category' not in defaults:
        defaults.update({'category': category_factory(to_db=to_db)})
    if to_db:
        return Product.objects.create(**defaults)
    return Product(**defaults)


def attribute_factory(to_db=True, **kwargs):
    defaults = {
        'name': 'Size',
    }
    defaults.update(kwargs)
    if to_db:
        return Attribute.objects.create(**defaults)
    return Attribute(**defaults)


def product_attribute_value_factory(to_db=True, **kwargs):
    defaults = {
        'value': 'Red'
    }
    defaults.update(kwargs)
    if to_db:
        return ProductAttributeValue.objects.create(**defaults)
    return ProductAttributeValue(**defaults)