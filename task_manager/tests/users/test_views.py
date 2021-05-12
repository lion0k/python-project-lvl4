"""User views tests."""
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from task_manager.users.views import UserListView
from task_manager.utils import load_file_from_fixture


class TestListViewCase(TestCase):
    """Test listing view."""

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        number_of_users = 15
        cls.list_view_class = UserListView
        cls.user_model = get_user_model()
        for postfix in range(number_of_users):
            user = {'username': 'user{postfix}'.format(postfix=postfix)}
            cls.user_model.objects.create(**user)

    def test_view_url(self):
        """Test view url."""
        self.assertEqual(reverse('users'), '/users/')

        response = self.client.get(reverse('users'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_view_uses_correct_template(self):
        """Test view uses correct template."""
        response = self.client.get(reverse('users'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'users/index.html')

    def test_pagination_first_page(self):
        """Test pagination."""
        response = self.client.get(reverse('users'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertTrue(
            len(response.context['users_list']) == self.list_view_class.paginate_by,  # noqa: E501
        )

    def test_pagination_last_page(self):
        """Test pagination."""
        count_recs = self.user_model.objects.count()
        count_rec_last_page = count_recs % self.list_view_class.paginate_by
        if count_rec_last_page:
            last_page = (count_recs // self.list_view_class.paginate_by) + 1
        else:
            last_page = count_recs // self.list_view_class.paginate_by
            count_rec_last_page = self.list_view_class.paginate_by

        response = self.client.get(
            '{url}?page={page}'.format(url=reverse('users'), page=last_page),
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertTrue(
            len(response.context['users_list']) == count_rec_last_page,
        )


class TestCreateViewCase(TestCase):
    """Test create view."""

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        cls.users_data = load_file_from_fixture(
            filename='test_users_data.json',
            add_paths=['users'],
        )
        cls.user_model = get_user_model()

    def test_create_view(self):
        """Test check view create model."""
        response = self.client.get(reverse('create_user'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'users/create.html')

        user = self.users_data['user_insert']
        response = self.client.post(
            path=reverse('create_user'),
            data=user,
        )
        self.assertRedirects(response, reverse('login'))
        user_in_db = self.user_model.objects.get(username=user['username'])
        self.assertEqual(user['username'], user_in_db.username)
        self.assertEqual(user['first_name'], user_in_db.first_name)
        self.assertEqual(user['last_name'], user_in_db.last_name)


class TestLoginLogoutViewCase(TestCase):
    """Test login and logout user."""

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        cls.users_data = load_file_from_fixture(
            filename='test_users_data.json',
            add_paths=['users'],
        )
        cls.user_model = get_user_model()
        cls.user = cls.users_data['user']
        cls.user_model.objects.create_user(**cls.user)

    def test_login(self):
        """Test login user."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'users/login.html')

        self.assertTrue(
            self.user_model.objects.filter(
                username=self.user['username'],
            ).exists()  # noqa: C812
        )
        response = self.client.post(
            path=reverse('login'),
            data=self.user,
            follow=True,
        )
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(response.context['user'].is_authenticated)

    def test_logout(self):
        """Test logout user."""
        response = self.client.get(reverse('logout'), follow=True)
        self.assertRedirects(response, reverse('home'))
        self.assertFalse(response.context['user'].is_authenticated)


class TestUpdateCase(TestCase):
    """Test update view."""

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        cls.users_data = load_file_from_fixture(
            filename='test_users_data.json',
            add_paths=['users'],
        )
        cls.user_model = get_user_model()
        cls.credentials = cls.users_data['user']
        cls.user = cls.user_model.objects.create_user(**cls.credentials)

    def setUp(self) -> None:
        """Setup always when test executed."""
        self.client.login(**self.credentials)

    def test_update_view(self):
        """Test check view update model."""
        response = self.client.post(
            path=reverse('update_user', args=[self.user.pk]),
            data=self.users_data['user_update'],
        )
        self.assertRedirects(response, reverse('users'))
        user_in_db = self.user_model.objects.get(pk=self.user.pk)
        self.assertEqual(
            self.users_data['user_update']['username'], user_in_db.username,
        )
        self.assertEqual(
            self.users_data['user_update']['first_name'], user_in_db.first_name,
        )
        self.assertEqual(
            self.users_data['user_update']['last_name'], user_in_db.last_name,
        )

    def test_update_user_without_permission(self):
        """Test update user without permission."""
        user2 = self.user_model.objects.create(
            **self.users_data['user2'],
        )
        response = self.client.post(
            path=reverse('update_user', args=[user2.pk]),
            data=self.users_data['user_update'],
        )
        self.assertRedirects(response, reverse('users'))
        self.assertNotEqual(
            self.users_data['user_update']['username'],
            self.user_model.objects.get(pk=user2.pk).username,
        )


class TestDeleteCase(TestCase):
    """Test delete view."""

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        cls.users_data = load_file_from_fixture(
            filename='test_users_data.json',
            add_paths=['users'],
        )
        cls.user_model = get_user_model()
        cls.credentials = cls.users_data['user']
        cls.user = cls.user_model.objects.create_user(**cls.credentials)

    def setUp(self) -> None:
        """Setup always when test executed."""
        self.client.login(**self.credentials)

    def test_delete_view(self):
        """Test check view delete model."""
        response = self.client.post(
            path=reverse('delete_user', args=[self.user.pk]),
        )
        self.assertRedirects(response, reverse('users'))
        self.assertFalse(
            self.user_model.objects.filter(
                username=self.credentials['username'],
            ).exists()  # noqa: C812
        )

    def test_delete_user_without_permission(self):
        """Test delete user without permission."""
        user2 = self.user_model.objects.create(
            **self.users_data['user2'],
        )
        response = self.client.post(
            path=reverse('delete_user', args=[user2.pk]),
        )
        self.assertRedirects(response, reverse('users'))
        self.assertTrue(
            self.user_model.objects.filter(
                username=user2.username,
            ).exists()  # noqa: C812
        )
