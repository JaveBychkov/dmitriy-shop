from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.html import strip_tags


def get_email_obj(subject, context, template, mail_to):
    """
    Return the instance of EmailMultiAlternative email with attached html
    template that was rendered with given context.

    Parameters
    ----------
    subject : str
        The subject of a mail.
    context : dict
        The context with which given template should be rendered.
    template : str
        Path to template.
    mail_to : iterable
        The list of emails that should be emailed.

    Returns
    -------
    EmailMultiAlternatives
        instance of email.
    """
    html_body = loader.render_to_string(template, context)
    text_body = strip_tags(html_body)
    email = EmailMultiAlternatives(
        subject, text_body, to=mail_to,
        alternatives=[(html_body, 'text/html')]
    )
    return email