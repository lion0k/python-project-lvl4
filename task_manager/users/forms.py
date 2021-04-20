"""User forms."""
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class CustomUserCreationForm(UserCreationForm):
    """User creation form."""

    class Meta:
        """Meta information."""

        model = get_user_model()
        fields = [
            'first_name',
            'last_name',
            'username',
            'password1',
            'password2',
        ]
