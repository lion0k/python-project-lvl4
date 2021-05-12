"""Labels views tests."""
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from task_manager.labels.models import Label
from task_manager.labels.views import LabelListView


class TestListViewCase(TestCase):
    """Test listing view."""

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        number_of_labels = 15
        cls.model = Label
        cls.list_view_class = LabelListView
        cls.model.objects.bulk_create(
            [
                cls.model(
                    name=f'task{postfix}',  # noqa: WPS305
                ) for postfix in range(number_of_labels)
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
        self.assertEqual(reverse('labels'), '/labels/')

        response = self.client.get(reverse('labels'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_view_uses_correct_template(self):
        """Test view uses correct template."""
        response = self.client.get(reverse('labels'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'labels/index.html')

    def test_pagination_first_page(self):
        """Test pagination."""
        response = self.client.get(reverse('labels'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertTrue(
            len(response.context['labels_list']) == self.list_view_class.paginate_by,
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
            '{url}?page={page}'.format(url=reverse('labels'), page=last_page),
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertTrue(len(response.context['labels_list']) == count_rec_last_page)

    def test_not_auth_users_cannot_view(self):
        """Test not authenticated users not allowed view."""
        self.client.logout()
        response = self.client.get(reverse('labels'))
        self.assertRedirects(response, reverse('login'))


class TestCreateViewCase(TestCase):
    """Test create view."""

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        cls.data = {'name': 'test'}
        cls.model = Label
        cls.user_model = get_user_model()
        cls.credentials = {'username': 'test', 'password': 'test'}
        cls.user_model.objects.create_user(**cls.credentials)

    def setUp(self):
        """Setup always when test executed."""
        self.client.login(**self.credentials)

    def test_create_view(self):
        """Test check view create model."""
        response = self.client.get(reverse('create_label'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'labels/create.html')

        response = self.client.post(
            path=reverse('create_label'),
            data=self.data,
        )
        self.assertRedirects(response, reverse('labels'))
        self.assertEqual(
            self.data['name'],
            self.model.objects.get(name=self.data['name']).name,
        )

    def test_cannot_create(self):
        """Test check unique field."""
        response = self.client.post(
            path=reverse('create_label'),
            data=self.data,
        )
        self.assertRedirects(response, reverse('labels'))
        count_labels = self.model.objects.all().count()

        response = self.client.post(
            path=reverse('create_label'),
            data=self.data,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(count_labels, self.model.objects.all().count())

    def test_get_not_auth_users_cannot_create(self):
        """Test GET not authenticated users cannot create."""
        self.client.logout()
        response = self.client.get(reverse('create_label'))
        self.assertRedirects(response, reverse('login'))

    def test_post_not_auth_users_cannot_create(self):
        """Test POST not authenticated users cannot create."""
        self.client.logout()
        response = self.client.post(reverse('create_label'))
        self.assertRedirects(response, reverse('login'))


class TestUpdateCase(TestCase):
    """Test update view."""

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        cls.model = Label
        cls.user_model = get_user_model()
        cls.data = {'name': 'test'}
        cls.credentials = {'username': 'test', 'password': 'test'}
        cls.label = cls.model.objects.create(**cls.data)
        cls.user_model.objects.create_user(**cls.credentials)

    def setUp(self) -> None:
        """Setup always when test executed."""
        self.client.login(**self.credentials)

    def test_update_view(self):
        """Test check view update model."""
        data_for_update = {'name': 'another_label'}
        response = self.client.post(
            path=reverse('update_label', args=[self.label.pk]),
            data=data_for_update,
        )
        self.assertRedirects(response, reverse('labels'))
        self.assertEqual(
            data_for_update['name'],
            self.model.objects.get(pk=self.label.pk).name,
        )

    def test_cannot_update(self):
        """Test check unique field."""
        another_label_data = {'name': 'another_name'}
        another_label_created = self.model.objects.create(
            **another_label_data,
        )
        response = self.client.post(
            path=reverse('update_label', args=[another_label_created.pk]),
            data=self.data,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_get_not_auth_users_cannot_update(self):
        """Test GET not authenticated users cannot update."""
        self.client.logout()
        response = self.client.get(
            reverse('update_label', args=[self.label.pk]),
        )
        self.assertRedirects(response, reverse('login'))

    def test_post_not_auth_users_cannot_update(self):
        """Test POST not authenticated users cannot update."""
        self.client.logout()
        response = self.client.post(
            reverse('update_label', args=[self.label.pk]),
        )
        self.assertRedirects(response, reverse('login'))


class TestDeleteCase(TestCase):
    """Test delete view."""

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        cls.model = Label
        cls.user_model = get_user_model()
        cls.data = {'name': 'test'}
        cls.credentials = {'username': 'test', 'password': 'test'}
        cls.label = cls.model.objects.create(**cls.data)
        cls.user_model.objects.create_user(**cls.credentials)

    def setUp(self) -> None:
        """Setup always when test executed."""
        self.client.login(**self.credentials)

    def test_delete_view(self):
        """Test check view delete model."""
        response = self.client.post(
            path=reverse('delete_label', args=[self.label.pk]),
        )
        self.assertRedirects(response, reverse('labels'))
        self.assertFalse(
            self.model.objects.filter(name=self.data['name']).exists()  # noqa: C812
        )

    def test_get_not_auth_users_cannot_delete(self):
        """Test GET not authenticated users cannot delete."""
        self.client.logout()
        response = self.client.get(
            reverse('delete_label', args=[self.label.pk]),
        )
        self.assertRedirects(response, reverse('login'))

    def test_post_not_auth_users_cannot_delete(self):
        """Test POST not authenticated users cannot delete."""
        self.client.logout()
        response = self.client.post(
            reverse('delete_label', args=[self.label.pk]),
        )
        self.assertRedirects(response, reverse('login'))
