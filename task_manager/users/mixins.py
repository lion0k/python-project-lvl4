"""Users mixins."""
from task_manager.mixins import CheckUserRightsTestMixin


class UserIsHimselfMixin(CheckUserRightsTestMixin):
    """Deny a request with a permission error if the test_func() == False."""

    def test_func(self) -> bool:
        """
        Test function.

        Returns:
            bool:
        """
        return self.get_object() == self.request.user
