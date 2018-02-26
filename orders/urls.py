from django.urls import path

from .views import CheckOrderView, PlaceOrderView


app_name = 'orders'


urlpatterns = [
    path('check_order/', CheckOrderView.as_view(), name='check-order'),
    path('place_order/', PlaceOrderView.as_view(), name='place-order')
]