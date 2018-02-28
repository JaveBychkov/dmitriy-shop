from django import template

from onlineshop.models import Category

register = template.Library()


@register.inclusion_tag('onlineshop/_category_menu.html')
def category_menu():
    categories = Category.objects.exclude(title='Unassigned')
    return {'nodes': categories}