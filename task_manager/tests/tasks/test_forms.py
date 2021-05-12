"""Statuses forms tests."""
from django.test import TestCase
from task_manager.statuses.forms import StatusForm


class TestStatusCreationForm(TestCase):
    """Test form validations."""

    def test_valid_form(self):
        """Test form is valid."""
        data = {'name': 'test'}
        self.assertTrue(StatusForm(data=data).is_valid())

    def test_invalid_form(self):
        """Test form is invalid."""
        data = {'name': ''}
        self.assertFalse(StatusForm(data=data).is_valid())
