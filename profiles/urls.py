from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy


from .views import (update_profile,
                    CopySessionCartAfterLoginView, RegistrationView)


# to easily do reverse: reverse(onlineshop:home)
app_name = 'profiles'

urlpatterns = [
    path('', update_profile, name='detail'),
    path('login/',
         CopySessionCartAfterLoginView.as_view(
             template_name='profiles/login.html'),
         name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('password_reset/',
         auth_views.PasswordResetView.as_view(
             template_name='profiles/password_reset.html',
             success_url=reverse_lazy('onlineshop:home'),
             email_template_name='profiles/password_reset_email.html'
         ), name='password_reset'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='profiles/password_reset_confirm.html',
             success_url=reverse_lazy('profiles:login'),
         ),
         name='password_reset_confirm')
]
