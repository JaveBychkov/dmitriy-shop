from orders.utils import get_email_obj


def test_get_email_obj_returns_email_obj(mailoutbox):
    template = 'orders/emails/email_for_user.html'
    email = get_email_obj(
        'Subject', {}, template, ['someone@mail.com'])

    assert email.subject == 'Subject'
    assert email.to == ['someone@mail.com']
    assert email.alternatives[0][1] == 'text/html'
