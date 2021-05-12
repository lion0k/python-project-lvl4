"""Statuses views tests."""
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from task_manager.statuses.models import Status
from task_manager.statuses.views import StatusListView


class TestListViewCase(TestCase):
    """Test listing view."""

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        number_of_status = 15
        cls.model = Status
        cls.list_view_class = StatusListView
        cls.model.objects.bulk_create(
            [
                cls.model(
                    name=f'task{postfix}',  # noqa: WPS305
                ) for postfix in range(number_of_status)
            ],
        )
        cls.user_model = get_user_model()
        cls.credentials = {'username': 'test', 'password': 'test'}
        cls.user_model.objects.create_user(**cls.credentials)

    def setUp(self):
        """Setup always when test executed."""
        self.client.login(**self.credentials)

    def test_view_url(self):
        """Test view url."""
        self.assertEqual(reverse('statuses'), '/statuses/')

        response = self.client.get(reverse('statuses'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_view_uses_correct_template(self):
        """Test view uses correct template."""
        response = self.client.get(reverse('statuses'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'statuses/index.html')

    def test_pagination_first_page(self):
        """Test pagination."""
        response = self.client.get(reverse('statuses'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertTrue(
            len(response.context['statuses_list']) == self.list_view_class.paginate_by,  # noqa: E501
        )

    def test_pagination_last_page(self):
        """Test pagination."""
        count_recs = self.model.objects.count()
        count_rec_last_page = count_recs % self.list_view_class.paginate_by
        if count_rec_last_page:
            last_page = (count_recs // self.list_view_class.paginate_by) + 1
        else:
            last_page = count_recs // self.list_view_class.paginate_by
            count_rec_last_page = self.list_view_class.paginate_by

        response = self.client.get(
            '{url}?page={page}'.format(url=reverse('statuses'), page=last_page),
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertTrue(
            len(response.context['statuses_list']) == count_rec_last_page,
        )

    def test_not_auth_users_cannot_view(self):
        """Test not authenticated users not allowed view."""
        self.client.logout()
        response = self.client.get(reverse('statuses'))
        self.assertRedirects(response, reverse('login'))


class TestCreateViewCase(TestCase):
    """Test create view."""

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        cls.data = {'name': 'test'}
        cls.model = Status
        cls.user_model = get_user_model()
        cls.credentials = {'username': 'test', 'password': 'test'}
        cls.user_model.objects.create_user(**cls.credentials)

    def setUp(self):
        """Setup always when test executed."""
        self.client.login(**self.credentials)

    def test_create_view(self):
        """Test check view create model."""
        response = self.client.get(reverse('create_status'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'statuses/create.html')

        response = self.client.post(
            path=reverse('create_status'),
            data=self.data,
        )
        self.assertRedirects(response, reverse('statuses'))
        self.assertEqual(
            self.data['name'],
            self.model.objects.get(name=self.data['name']).name,
        )

    def test_cannot_create(self):
        """Test check unique field."""
        response = self.client.post(
            path=reverse('create_status'),
            data=self.data,
        )
        self.assertRedirects(response, reverse('statuses'))
        count_tasks = Status.objects.all().count()

        response = self.client.post(
            path=reverse('create_status'),
            data=self.data,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(count_tasks, Status.objects.all().count())

    def test_get_not_auth_users_cannot_create(self):
        """Test GET not authenticated users cannot create."""
        self.client.logout()
        response = self.client.get(reverse('create_status'))
        self.assertRedirects(response, reverse('login'))

    def test_post_not_auth_users_cannot_create(self):
        """Test POST not authenticated users cannot create."""
        self.client.logout()
        response = self.client.post(reverse('create_status'))
        self.assertRedirects(response, reverse('login'))


class TestUpdateCase(TestCase):
    """Test update view."""

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        cls.model = Status
        cls.user_model = get_user_model()
        cls.data = {'name': 'test'}
        cls.credentials = {'username': 'test', 'password': 'test'}
        cls.status = cls.model.objects.create(**cls.data)
        cls.user_model.objects.create_user(**cls.credentials)

    def setUp(self) -> None:
        """Setup always when test executed."""
        self.client.login(**self.credentials)

    def test_update_view(self):
        """Test check view update model."""
        data_for_update = {'name': 'another_status'}
        response = self.client.post(
            path=reverse('update_status', args=[self.status.pk]),
            data=data_for_update,
        )
        self.assertRedirects(response, reverse('statuses'))
        self.assertEqual(
            data_for_update['name'],
            self.model.objects.get(pk=self.status.pk).name,
        )

    def test_cannot_update(self):
        """Test check unique field."""
        another_status_data = {'name': 'another_name'}
        another_status_created = self.model.objects.create(
            **another_status_data,
        )
        response = self.client.post(
            path=reverse('update_status', args=[another_status_created.pk]),
            data=self.data,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_get_not_auth_users_cannot_update(self):
        """Test GET not authenticated users cannot update."""
        self.client.logout()
        response = self.client.get(
            reverse('update_status', args=[self.status.pk]),
        )
        self.assertRedirects(response, reverse('login'))

    def test_post_not_auth_users_cannot_update(self):
        """Test POST not authenticated users cannot update."""
        self.client.logout()
        response = self.client.post(
            reverse('update_status', args=[self.status.pk]),
        )
        self.assertRedirects(response, reverse('login'))


class TestDeleteCase(TestCase):
    """Test delete view."""

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        cls.model = Status
        cls.user_model = get_user_model()
        cls.data = {'name': 'test'}
        cls.credentials = {'username': 'test', 'password': 'test'}
        cls.status = cls.model.objects.create(**cls.data)
        cls.user_model.objects.create_user(**cls.credentials)

    def setUp(self) -> None:
        """Setup always when test executed."""
        self.client.login(**self.credentials)

    def test_delete_view(self):
        """Test check view delete model."""
        response = self.client.post(
            path=reverse('delete_status', args=[self.status.pk]),
        )
        self.assertRedirects(response, reverse('statuses'))
        self.assertFalse(
            self.model.objects.filter(name=self.data['name']).exists(),
        )

    def test_get_not_auth_users_cannot_delete(self):
        """Test GET not authenticated users cannot delete."""
        self.client.logout()
        response = self.client.get(
            reverse('delete_status', args=[self.status.pk]),
        )
        self.assertRedirects(response, reverse('login'))

    def test_post_not_auth_users_cannot_delete(self):
        """Test POST not authenticated users cannot delete."""
        self.client.logout()
        response = self.client.post(
            reverse('delete_status', args=[self.status.pk]),
        )
        self.assertRedirects(response, reverse('login'))
