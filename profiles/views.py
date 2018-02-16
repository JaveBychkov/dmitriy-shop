from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import ugettext as _
from django.views import generic

from shoppingcart.models import Cart, Line

from .forms import AddressForm, UserForm, UserWEmailCreationForm


@login_required
def update_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        address_form = AddressForm(request.POST, instance=request.user.address)
        if user_form.is_valid() and address_form.is_valid():
            user_form.save()
            address_form.save()
            messages.success(
                request, _('Your profile was successfully updated!')
            )
            return redirect('profiles:detail')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        user_form = UserForm(instance=request.user)
        address_form = AddressForm(instance=request.user.address)
    return render(request, 'profiles/profile.html', {
        'user_form': user_form,
        'address_form': address_form
    })


class CopySessionCartAfterLoginView(LoginView):

    # TODO: Consider using separate redirect view.

    redirect_authenticated_user = True

    def form_valid(self, form):
        """
        If user has session cart - take all lines from his session cart
        and insert it into cart that associated with user
        """
        user = form.get_user()
        login(self.request, user)

        cart_id = self.request.session.pop('cart_id', None)
        if cart_id is not None:
            user_cart = Cart.objects.get_or_create(owner=user)[0]

            lines = Line.objects.filter(
                cart__in=[cart_id, user_cart.pk]
            ).order_by('product_id').distinct('product')

            user_cart.line_set.set(lines, clear=True)
        return HttpResponseRedirect(self.get_success_url())


class RegistrationView(generic.CreateView):

    form_class = UserWEmailCreationForm
    template_name = 'profiles/registration.html'
    success_url = reverse_lazy('profiles:login')
