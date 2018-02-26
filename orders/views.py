from django.conf import settings
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core import mail
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect
from django.template import loader
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.translation import ugettext as _
from django.views import generic

from profiles.forms import AddressForm
from shoppingcart.models import Cart

from .forms import UserForm
from .models import Order
from .tasks import send_order_placed_email


class NotEmptyCartRequiredMixin:

    def dispatch(self, request, *args, **kwargs):
        user_and_session = request.user, request.session
        cart = Cart.objects.get_full_cart(*user_and_session)
        if not cart.line_set.exists():
            messages.error(
                request, _('You can\'t place orders with empty cart')
            )
            return redirect('onlineshop:home')
        self.cart = cart
        return super().dispatch(request, *args, **kwargs)


class PlaceOrderView(NotEmptyCartRequiredMixin, generic.TemplateView):

    form_classes = {'user': UserForm, 'address': AddressForm}
    template_name = 'orders/place_order.html'

    def get(self, request, *args, **kwargs):

        if request.user.is_authenticated:
            user = request.user
            address = user.address
            forms = {
                'user': UserForm(instance=user),
                'address': AddressForm(instance=address)
            }
        else:
            forms = {
                'user': UserForm(),
                'address': AddressForm()
            }
        return self.render_to_response(self.get_context_data(forms=forms))

    def post(self, request, *args, **kwargs):
        forms = {
            'user': UserForm(request.POST),
            'address': AddressForm(request.POST)
        }
        if all([x.is_valid() for x in forms.values()]):
            form_data = {'user': forms['user'].cleaned_data,
                         'address': forms['address'].cleaned_data}
            self.request.session['form'] = form_data
            return redirect('orders:check-order')
        return self.render_to_response(self.get_context_data(forms=forms))


class CheckOrderView(NotEmptyCartRequiredMixin, generic.TemplateView):

    template_name = 'orders/check_order.html'
    email_templates = {'user': 'orders/emails/email_for_user.html',
                       'manager': 'orders/emails/email_for_manager.html'}

    def dispatch(self, request, *args, **kwargs):
        self.form_data = request.session.get('form')

        if self.form_data is None:
            messages.warning(request, _('Please fill out form to continue'))
            return redirect('orders:place-order')

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        order = Order.objects.create_order_instance(self.form_data)
        return self.render_to_response(self.get_context_data(order=order))

    def post(self, request, *args, **kwargs):

        order = Order.objects.create_order_instance(self.form_data)
        order.from_cart_to_order(self.cart)

        self.send_email(order)

        messages.success(
            request,
            _('Your order now proccessing! Information will be sent to email.')
        )
        request.session.pop('form', None)
        return redirect('onlineshop:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = self.cart
        context['total'] = self.cart.get_total_price()
        return context

    def send_email(self, order):
        site_name = get_current_site(self.request).name
        object_link = self.request.build_absolute_uri(
            reverse('admin:orders_order_change', args=(order.pk,))
        )
        context = {'order': order.pk, 'site_name': site_name,
                   'admin_link': object_link}
        subject = _("Order placed on 3DShop")

        # Celery task.
        send_order_placed_email.delay(subject, context, self.email_templates)
