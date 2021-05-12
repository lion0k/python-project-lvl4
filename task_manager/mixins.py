"""Mixins."""
from typing import Any

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
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


class CheckUserRightsTestMixin(UserPassesTestMixin):
    """Deny a request with a permission error if the test_func() == False."""

    redirect_url = ''
    error_message = ''

    def handle_no_permission(self) -> HttpResponseRedirect:
        """
        Handle no permission.

        Returns:
            Union:
        """
        redirect_url = self.redirect_url or settings.LOGIN_REDIRECT_URL
        return redirect(redirect_url)

    def dispatch(self, request, *args, **kwargs) -> Any:
        """
        Dispatch.

        Args:
            request:

        Returns:
            Any:
        """
        user_test_result = self.get_test_func()()

        if not user_test_result:
            messages.error(request, self.error_message)
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
