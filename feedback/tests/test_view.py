import pytest

from django.urls import reverse
from django.utils import translation


@pytest.mark.django_db
class TestFeedbackView:

    def test_get_request_returns_empty_form(self, client):
        response = client.get(reverse('feedback'))

        assert response.status_code == 200
        assert response.context.get('form') is not None
        assert response.context['form'].initial == {}

    def test_get_request_returns_form_with_initial(self, client, admin_user):
        """Returns form with initial for authenticated users."""

        client.force_login(admin_user)

        response = client.get(reverse('feedback'))

        initial = {
            'name': admin_user.get_full_name(), 'email': admin_user.email
        }

        assert response.status_code == 200
        assert response.context.get('form') is not None
        assert response.context['form'].initial == initial

    def test_valid_post_request(self, client, data, mailoutbox):
        with translation.override('en'):
            response = client.post(reverse('feedback'), data, follow=True)
        msg = 'Thank you for your feedback!'
        assert response.status_code == 200
        assert response.context.get('messages') is not None
        messages = list(response.context['messages'])
        assert len(messages) == 1
        assert messages[0].message == msg
        assert len(mailoutbox) == 1

    def test_invalid_post_request(self, client, data, mailoutbox):
        data['email'] = 'invalidemail'

        response = client.post(reverse('feedback'), data)

        assert response.status_code == 200
        assert response.context['form'].is_valid() is False
        assert response.context['form'].errors.get('email') is not None
