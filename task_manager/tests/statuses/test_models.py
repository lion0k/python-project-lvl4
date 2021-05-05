"""Statuses model tests."""
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.deletion import ProtectedError
from task_manager.mixins import TestCaseWithoutRollbar
from task_manager.statuses.models import Status


class TestModelCase(TestCaseWithoutRollbar):
    """Test model case."""

    fixtures = [
        'tasks/db_users.json',
        'tasks/db_statuses.json',
        'tasks/db_labels.json',
        'tasks/db_tasks.json',
    ]

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        cls.data = {'name': 'test'}
        cls.model = Status

    def setUp(self) -> None:
        """Setup always when test executed."""
        self.model.objects.create(**self.data)

    def test_create(self):
        """Test check create model."""
        status = self.model.objects.get(**self.data)
        self.assertTrue(isinstance(status, self.model))
        self.assertEqual(self.data['name'], status.name)

    def test_update(self):
        """Test check update model."""
        status = self.model.objects.get(**self.data)
        update_status = 'another_name'
        status.username = update_status
        status.save()
        self.assertEqual(update_status, status.username)

    def test_delete(self):
        """Test check delete model."""
        status = self.model.objects.get(**self.data)
        status.delete()
        with self.assertRaises(ObjectDoesNotExist):
            self.model.objects.get(pk=status.id)

    def test_name_field_protection(self):
        """Test 'name' field protection."""
        label_in_db = self.model.objects.get(name='new')
        with self.assertRaises(ProtectedError):
            label_in_db.delete()
