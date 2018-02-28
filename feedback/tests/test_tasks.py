from django.utils import translation

from feedback.tasks import send_feedback


def test_send_feedback_sends_mail(mailoutbox, data, settings):
    settings.MANAGERS = (('manager', 'manager@mail.com'),)

    with translation.override('en'):
        send_feedback(data)

    assert len(mailoutbox) == 1
    m = mailoutbox[0]
    subject = '[Django] Message from Name. Email: example@email.com'
    assert m.to == ['manager@mail.com']
    assert m.subject == subject
    assert m.body == data['message']