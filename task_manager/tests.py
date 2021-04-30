"""Project tests."""
from django import test
from django.http.response import HttpResponseBase
from django.urls import reverse


@test.modify_settings(MIDDLEWARE={'remove': [
    'rollbar.contrib.django.middleware.RollbarNotifierMiddleware',
]})
class TestI18nCase(test.TestCase):
    """Language tests."""

    def test_i18_ru(self):
        """Test correct get RU language."""
        headers = {'HTTP_ACCEPT_LANGUAGE': 'ru'}
        name_project = 'Менеджер задач'
        response = self.client.get(reverse('users'), **headers)
        self.assertEqual(response.status_code, HttpResponseBase.status_code)
        self.assertTrue(name_project in response.content.decode('utf-8'))

    def test_i18_en(self):
        """Test correct get EN language."""
        headers = {'HTTP_ACCEPT_LANGUAGE': 'en'}
        name_project = 'Task Manager'
        response = self.client.get(reverse('users'), **headers)
        self.assertEqual(response.status_code, HttpResponseBase.status_code)
        self.assertTrue(name_project in response.content.decode('utf-8'))
