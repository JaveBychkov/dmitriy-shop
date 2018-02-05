from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import Category, Product, ProductAttributeValue


class EnsureCsrfCookieMixin:
    """
    Ensures that the CSRF cookie will be passed to the client.
    """

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super(EnsureCsrfCookieMixin, self).dispatch(*args, **kwargs)


class OnlineShopHomePageView(EnsureCsrfCookieMixin, generic.ListView):

    model = Product
    template_name = 'onlineshop/index.html'
    context_object_name = 'products'
    paginate_by = 6


class CategoryDetailView(EnsureCsrfCookieMixin, generic.DetailView):
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


class ProductDetailView(EnsureCsrfCookieMixin, generic.DetailView):
    model = Product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attributes'] = ProductAttributeValue.objects.filter(
            product=self.object
        ).select_related('attribute')
        return context
