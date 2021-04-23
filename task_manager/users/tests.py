"""Users tests."""
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponseBase
from django.test import TestCase
from django.urls import reverse
from task_manager.users.forms import CustomUserCreationForm
from task_manager.utils import load_file_from_fixture


class TestModelCase(TestCase):
    """Test model case."""

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        cls.credentials = {'username': 'testing_user'}
        cls.user_model = get_user_model()

    def setUp(self) -> None:
        """Setup always when test executed."""
        self.user_model.objects.create(**self.credentials)

    def test_create(self):
        """Test check create model."""
        user = self.user_model.objects.get(**self.credentials)
        self.assertTrue(isinstance(user, self.user_model))
        self.assertEqual(self.credentials['username'], user.username)

    def test_update(self):
        """Test check update model."""
        user = self.user_model.objects.get(**self.credentials)
        update_name = 'another_name'
        user.username = update_name
        user.save()
        self.assertEqual(update_name, user.username)

    def test_delete(self):
        """Test check delete model."""
        user = self.user_model.objects.get(**self.credentials)
        user.delete()
        with self.assertRaises(ObjectDoesNotExist):
            self.user_model.objects.get(pk=user.id)


class TestListViewCase(TestCase):
    """Test listing view."""

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        number_of_users = 15
        cls.user_model = get_user_model()
        for postfix in range(number_of_users):
            user = {'username': 'user{postfix}'.format(postfix=postfix)}
            cls.user_model.objects.create(**user)

    def test_view_url_exists_at_desired_location(self):
        """Test view url exists at desired location."""
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, HttpResponseBase.status_code)

    def test_view_url_accessible_by_name(self):
        """Test view url accessible by name."""
        response = self.client.get(reverse('users'))
        self.assertEqual(response.status_code, HttpResponseBase.status_code)

    def test_view_uses_correct_template(self):
        """Test view uses correct template."""
        response = self.client.get(reverse('users'))
        self.assertEqual(response.status_code, HttpResponseBase.status_code)
        self.assertTemplateUsed(response, 'users/index.html')

    def test_pagination_is_ten(self):
        """Test pagination is ten."""
        response = self.client.get(reverse('users'))
        self.assertEqual(response.status_code, HttpResponseBase.status_code)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertTrue(len(response.context['users_list']) == 10)

    def test_lists_all_users(self):
        """Test lists all users."""
        response = self.client.get(
            '{url}?page=2'.format(url=reverse('users')),
        )
        self.assertEqual(response.status_code, HttpResponseBase.status_code)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertTrue(len(response.context['users_list']) == 5)

    def test_i18_ru(self):
        """Test correct get language."""
        headers = {'HTTP_ACCEPT_LANGUAGE': 'ru'}
        name_project = 'Менеджер задач'
        response = self.client.get(reverse('users'), **headers)
        self.assertEqual(response.status_code, HttpResponseBase.status_code)
        self.assertTrue(name_project in response.content.decode('utf-8'))

    def test_i18_en(self):
        """Test correct get language."""
        headers = {'HTTP_ACCEPT_LANGUAGE': 'en'}
        name_project = 'Task Manager'
        response = self.client.get(reverse('users'), **headers)
        self.assertEqual(response.status_code, HttpResponseBase.status_code)
        self.assertTrue(name_project in response.content.decode('utf-8'))


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
        self.assertEqual(response.status_code, HttpResponseBase.status_code)
        self.assertTemplateUsed(response, 'users/create.html')

        user = self.users_data['user_insert']
        response = self.client.post(
            path=reverse('create_user'),
            data=user,
        )
        self.assertRedirects(response, reverse('login'))
        self.assertEqual(
            user['username'],
            self.user_model.objects.get(username=user['username']).username,
        )


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
        self.assertEqual(response.status_code, HttpResponseBase.status_code)
        self.assertTemplateUsed(response, 'users/login.html')

        self.assertTrue(
            self.user_model.objects.filter(
                username=self.user['username'],
            ).exists(),
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


class TestUpdateDeleteCase(TestCase):
    """Test update and delete view."""

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
        self.assertRedirects(response, reverse('login'))
        self.assertEqual(
            self.users_data['user_update']['username'],
            self.user_model.objects.get(pk=self.user.pk).username,
        )

    def test_try_update_another_user(self):
        """Test cannot update data another user."""
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

    def test_delete_view(self):
        """Test check view delete model."""
        response = self.client.post(
            path=reverse('delete_user', args=[self.user.pk]),
        )
        self.assertRedirects(response, reverse('home'))
        self.assertFalse(
            self.user_model.objects.filter(
                username=self.credentials['username'],
            ).exists(),
        )

    def test_try_delete_another_user(self):
        """Test cannot delete data another user."""
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
            ).exists(),
        )


class TestCustomUserCreationForm(TestCase):
    """Test form validations."""

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        cls.users_data = load_file_from_fixture(
            filename='test_users_data.json',
            add_paths=['users'],
        )

    def test_valid_form(self):
        """Test form is valid."""
        data = self.users_data['valid_form']
        self.assertTrue(CustomUserCreationForm(data=data).is_valid())

    def test_invalid_form(self):
        """Test form is invalid."""
        data = self.users_data['invalid_form']
        self.assertFalse(CustomUserCreationForm(data=data).is_valid())
