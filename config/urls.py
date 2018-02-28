"""shop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


from remindme.views import add_reminder
from history.views import history_view
from feedback.views import feedback_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('remindme/', add_reminder, name='add-reminder'),
    path('feedback/', feedback_view, name='feedback'),
    path('orders/history/', history_view, name='order-history'),
    path('orders/', include('orders.urls')),
    path('cart/', include('shoppingcart.urls')),
    path('profile/', include('profiles.urls')),
    path('', include('onlineshop.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
