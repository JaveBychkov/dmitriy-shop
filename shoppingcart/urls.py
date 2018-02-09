from django.urls import path

from .views import (AddProductView, CartDetailView, RemoveProductView,
                    ChangeQuantityView, PriceChangedView)


app_name = 'shoppingcart'

urlpatterns = [
    path('add_product/', AddProductView.as_view(), name='add-product'),
    path('remove_product/', RemoveProductView.as_view(),
         name='remove-product'),
    path('update_quantity/', ChangeQuantityView.as_view(),
         name='update-quantity'),
    path('price_changed/', PriceChangedView.as_view(), name='price-changed'),
    path('detail/', CartDetailView.as_view(), name='cart-detail')
]
