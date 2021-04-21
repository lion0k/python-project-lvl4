"""Users tests."""
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from task_manager.utils import load_jsonfile_from_fixture
from django.utils.translation import gettext


class TestModelCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.credentials = {'username': 'testing_user'}
        cls.user_model = get_user_model()
        cls.test_user = cls.user_model.objects.create(**cls.credentials)

    def test_create(self):
        self.assertTrue(isinstance(self.test_user, self.user_model))
        self.assertEqual(self.credentials['username'], self.test_user.username)

    def test_update(self):
        update_name = 'another_name'
        self.test_user.username = update_name
        self.test_user.save()
        self.assertEqual(update_name, self.test_user.username)

    def test_delete(self):
        self.test_user.delete()
        with self.assertRaises(ObjectDoesNotExist):
            self.user_model.objects.get(pk=self.test_user.id)


class TestControllerCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.users_data = load_jsonfile_from_fixture(
            filename='test_users_data.json',
            add_paths=['users'],
        )
        cls.user_model = get_user_model()
        cls.client = Client()

    def test_list_view(self):
        for item in self.users_data.values():
            if 'password1' not in item:
                self.user_model.objects.create(**item)
        count_users_in_db = len(self.user_model.objects.all())
        response = self.client.get(reverse('users'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('users_list' in response.context)
        self.assertTemplateUsed(response, 'users/index.html')
        count_users_in_response = len(response.context['users_list'])
        self.assertEqual(count_users_in_db, count_users_in_response)
        self.assertTrue(gettext('Users') in response.content.decode('utf-8'))

    def test_create_view(self):
        response = self.client.get(reverse('create_user'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/create.html')

        user = self.users_data['user_for_insert']
        response = self.client.post(
            path=reverse('create_user'),
            data=user,
        )
        self.assertRedirects(response, reverse('login'))
        self.assertEqual(
            user['username'],
            self.user_model.objects.get(username=user['username']).username,
        )

    def test_update_view(self):
        # with out fixtures
        user_before = {"username": "valid_username", "password": "aqdvd23rd"}
        user_before_created = self.user_model.objects.create(**user_before)
        self.assertTrue(self.user_model.objects.filter(**user_before).exists())

        # self.client.login(username=user_before['username'], password=user_before['password'])
        response = self.client.post(
            path=reverse('login'),
            data=user_before,
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            path=reverse('update_user', args=[user_before_created.pk]),
            data={"username": "updated", 'password1': '12345678', 'password2': '12345678'},
        )
        # self.assertRedirects(response, reverse('home'))
