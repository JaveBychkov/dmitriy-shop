import pytest

from django.utils import translation

from orders.forms import UserForm


@pytest.fixture
def form():
    return UserForm()


class TestUserForm:

    def test_required_fields(self, form):
        assert len(form.fields) == 3
        assert all([field.required for field in form.fields.values()])

    def test_fields_length(self, form):
        max_length = 64
        assert all(
            [field.max_length == max_length for field in form.fields.values()]
            )

    def test_fields_labels(self, form):
        with translation.override('en'):
            assert form['first_name'].label == 'First Name'
            assert form['last_name'].label == 'Last Name'
            assert form['email'].label == 'Email'
