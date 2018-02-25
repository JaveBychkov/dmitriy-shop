import json

from django.http import JsonResponse, Http404
from django.utils.translation import ugettext as _
from onlineshop.models import Product

from .forms import ReminderForm


def add_reminder(request):
    if request.is_ajax():
        data = json.loads(request.body.decode('utf-8'))
        form = ReminderForm(data)
        form.fields['product'].queryset = Product.objects.filter(stock=0)

        ok_message = _('We will notify you as soon as product will go on sale')
        fail_message = _('Something went wrong, try again later')

        if form.is_valid():
            form.save()
            return JsonResponse({'message': ok_message})
        return JsonResponse({'message': fail_message}, status=404)
    raise Http404('Hmmmmm...')
