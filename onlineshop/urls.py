from django.urls import path

from .views import (OnlineShopHomePageView, CategoryDetailView,
                    ProductDetailView)


# to easily do reverse: reverse(onlineshop:home)
app_name = 'onlineshop'

urlpatterns = [
    path('', OnlineShopHomePageView.as_view(), name='home'),
    path('categories/<slug:slug>',
         CategoryDetailView.as_view(), name='category-detail'),
    path('products/<slug:slug>',
         ProductDetailView.as_view(), name='product-detail')
]
