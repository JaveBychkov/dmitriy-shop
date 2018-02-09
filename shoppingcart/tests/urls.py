from django.urls import include, path


urlpatterns = [
    path('cart/', include('shoppingcart.urls')),
]