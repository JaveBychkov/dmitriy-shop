from django.core.paginator import Paginator
from django.views import generic

from .models import Category, Product, ProductAttributeValue


class OnlineShopHomePageView(generic.ListView):

    model = Product
    template_name = 'onlineshop/index.html'
    context_object_name = 'products'
    paginate_by = 6
    ordering = '-date_added'

    def get_ordering(self):
        """Get ordering for products."""
        order = self.request.GET.get('order')
        default = super().get_ordering()

        ordering = {'new': '-date_added', 'discount': '-discount'}
        return ordering.get(order, default)


class CategoryDetailView(generic.DetailView):
    model = Category
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = self.get_paginator()
        return context

    def get_paginator(self):
        all_products = self.object.get_all_products()
        paginator = Paginator(all_products, self.paginate_by)
        page = self.request.GET.get('page')
        return paginator.get_page(page)


class ProductDetailView(generic.DetailView):
    model = Product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attributes'] = ProductAttributeValue.objects.filter(
            product=self.object
        ).select_related('attribute')
        return context
