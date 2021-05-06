"""Status mixins."""
from typing import Any, Union

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _


class CheckUserRightsTestMixin(UserPassesTestMixin):
    """Deny a request with a permission error if the test_func() == False."""

    redirect_url = ''

    def test_func(self) -> bool:
        """
        Test function.

        Returns:
            bool:
        """
        return self.get_object().creator == self.request.user

    def handle_no_permission(self) -> Union[  # noqa: WPS320
        HttpResponsePermanentRedirect,
        HttpResponseRedirect,
    ]:
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
            messages.error(request, _('ErrorTaskCanOnlyBeDeletedByAuthor'))
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
