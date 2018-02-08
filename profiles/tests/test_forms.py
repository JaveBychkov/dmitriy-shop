import pytest

from profiles.forms import UserWEmailCreationForm


class TestUserWEmailCreationForm:

    @pytest.mark.django_db
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

    @pytest.mark.django_db
    def test_save_method_saves_user_to_db_when_commit_eq_true(self):
        data = {
            'username': 'user', 'email': 'user@user.com',
            'password1': 'something123', 'password2': 'something123'
        }

        form = UserWEmailCreationForm(data)

        assert form.is_valid()

        user = form.save()

        assert getattr(user, 'pk') is not None