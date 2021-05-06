"""Mixins."""
from typing import Any

from django import test
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _


class CustomLoginRequiredMixin(LoginRequiredMixin):
    """Verify that the current user is authenticated."""

    redirect_field_name = ''

    def dispatch(self, request, *args, **kwargs) -> Any:
        """
        Dispatch.

        Args:
            request:

        Returns:
            Any:
        """
        if not request.user.is_authenticated:
            messages.error(request, _('UserNotAuthentication'))
            return redirect(settings.LOGIN_URL)
        return super().dispatch(request, *args, **kwargs)


@test.modify_settings(MIDDLEWARE={'remove': [
    'rollbar.contrib.django.middleware.RollbarNotifierMiddleware',
]})
class TestCaseWithoutRollbar(test.TestCase):
    """Switch off rollbar middleware."""
