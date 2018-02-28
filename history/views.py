from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.shortcuts import render

from orders.models import Order
from shoppingcart.models import Line


@login_required
def history_view(request):
    prefetch = Prefetch(
        'products', queryset=Line.objects.select_related('product')
    )
    qs = Order.objects.filter(
        user=request.user).prefetch_related(prefetch).order_by('-date')

    paginator = Paginator(qs, 3)
    page = request.GET.get('page')
    orders = paginator.get_page(page)

    return render(request, 'history/history.html', {'orders': orders})
