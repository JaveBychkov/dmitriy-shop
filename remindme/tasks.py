from django.utils.translation import ugettext as _

from config.celery import app

from orders.utils import get_email_obj

from .models import Reminder


@app.task
def send_notification_email(product_id, product_title, url):
    subject = _('{} have gone on sale!').format(product_title)

    qs = Reminder.objects.filter(product=product_id)

    emails = qs.values_list('email', flat=True)

    if not emails:
        return
    email = get_email_obj(subject, {'product': product_title, 'url': url},
                          'remindme/remind_email.html', emails)
    email.send()
    # Delete notifications.
    qs.delete()
