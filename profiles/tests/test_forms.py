import pytest

from django.core.exceptions import ValidationError

from profiles.forms import UserWEmailCreationForm, UserForm
from profiles.models import User


pytestmark = pytest.mark.django_db


class TestUserWEmailCreationForm:

    def test_save_method_assigns_email_to_user(self):
        data = {
            'username': 'user', 'email': 'user@user.com',
            'password1': 'something123', 'password2': 'something123'
        }

        form = UserWEmailCreationForm(data)

        assert form.is_valid()

        user = form.save(commit=False)

        assert user.email == 'user@user.com'
        assert getattr(user, 'pk') is None

    def test_save_method_saves_user_to_db_when_commit_eq_true(self):
        data = {
            'username': 'user', 'email': 'user@user.com',
            'password1': 'something123', 'password2': 'something123'
        }

        form = UserWEmailCreationForm(data)

        assert form.is_valid()

        user = form.save()

        assert getattr(user, 'pk') is not None

    def test_email_validation_not_raises_error(self):
        form = UserWEmailCreationForm()
        form.cleaned_data = {'email': 'some@mail.com'}
        email = form.clean_email()
        assert email == 'some@mail.com'

    def test_email_validation_raises_error(self, admin_user):
        # admin_user email is 'admin@example.com'.
        form = UserWEmailCreationForm()
        form.cleaned_data = {'email': admin_user.email}
        with pytest.raises(ValidationError):
            form.clean_email()


class TestUserForm:

    def test_email_validation_not_raises_error(self, admin_user):
        """Test that error won't be raisedif passed email is user email."""
        form = UserForm(instance=admin_user)
        form.cleaned_data = {'email': admin_user.email}
        email = form.clean_email()
        assert email == admin_user.email

    def test_email_validation_not_raises_error_if_available(self, admin_user):
        """Test that error won't be raised if passed email is available"""
        form = UserForm(instance=admin_user)
        form.cleaned_data = {'email': 'available@email.com'}
        email = form.clean_email()
        assert email == 'available@email.com'

    def test_email_validation_raises_error_on_update(self, admin_user):
        """
        Test taht error will be raised if passed email belong to another user.
        """
        form = UserForm(instance=admin_user)
        user = User.objects.create_user('somesome', 'some@mail.com')
        form.cleaned_data = {'email': user.email}
        with pytest.raises(ValidationError):
            form.clean_email()