from unittest.mock import patch

import pytest

from feedback.forms import FeedbackForm


@pytest.fixture
def feedback_form(data):
    return FeedbackForm(data)


class TestFeedbackForm:

    def test_get_sanitazied_data_method(self, feedback_form, data):
        assert feedback_form.is_valid() is True
        assert feedback_form.get_sanitazied_data() == data

    def test_send_feedback_email_method(self, feedback_form, mailoutbox, data):
        assert feedback_form.is_valid() is True
        with patch('feedback.forms.send_feedback.delay') as task:
            feedback_form.send_feedback_email()

            task.assert_called_with(data)
