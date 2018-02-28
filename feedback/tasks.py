from django.core.mail import mail_managers
from django.utils.translation import ugettext as _

from config.celery import app


@app.task
def send_feedback(data):
    """Send user message to managers."""
    subject = _('Message from {name}. Email: {email}').format(**data)

    mail_managers(subject, message=data['message'])
