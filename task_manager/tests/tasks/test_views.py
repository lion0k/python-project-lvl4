"""Tasks views tests."""
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from task_manager.statuses.models import Status
from task_manager.tasks.models import Tasks
from task_manager.tasks.views import TaskListView
from task_manager.utils import load_file_from_fixture


class TestListViewCase(TestCase):
    """Test listing view."""

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        number_of_tasks = 15
        cls.list_view_class = TaskListView
        cls.user_model = get_user_model()
        cls.model = Tasks
        cls.credentials = {'username': 'test', 'password': 'test'}
        cls.user = cls.user_model.objects.create_user(**cls.credentials)
        cls.status = Status.objects.create(name='test_status')
        cls.model.objects.bulk_create(
            [
                cls.model(
                    name=f'task{postfix}',  # noqa: WPS305
                    status=cls.status,
                    creator=cls.user,
                    executor=cls.user,
                ) for postfix in range(number_of_tasks)
            ],
        )

    def setUp(self):
        """Setup always when test executed."""
        self.client.login(**self.credentials)

    def test_view_url(self):
        """Test view url."""
        self.assertEqual(reverse('tasks'), '/tasks/')

        response = self.client.get(reverse('tasks'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_view_uses_correct_template(self):
        """Test view uses correct template."""
        response = self.client.get(reverse('tasks'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'tasks/index.html')

    def test_not_auth_users_cannot_view(self):
        """Test not authenticated users not allowed view."""
        self.client.logout()
        response = self.client.get(reverse('tasks'))
        self.assertRedirects(response, reverse('login'))

    def test_pagination_first_page(self):
        """Test pagination."""
        response = self.client.get(reverse('tasks'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertTrue(
            len(response.context['tasks_list']) == self.list_view_class.paginate_by,  # noqa: E501
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
            '{url}?page={page}'.format(url=reverse('tasks'), page=last_page),
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
        self.assertTrue(len(response.context['tasks_list']) == count_rec_last_page)

    def test_pagination_no_records(self):
        """Test pagination if records not exists."""
        self.model.objects.all().delete()
        response = self.client.get(reverse('tasks'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue('is_paginated' in response.context)
        self.assertFalse(response.context['is_paginated'])


class TestFilterViewCase(TestCase):
    """Test filter view."""

    fixtures = [
        'tasks/db_users.json',
        'tasks/db_statuses.json',
        'tasks/db_labels.json',
        'tasks/db_tasks.json',
    ]

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        cls.model = Tasks
        cls.user_model = get_user_model()
        cls.credentials = {'username': 'user_test1', 'password': '12345'}
        cls.url = reverse('tasks')
        cls.data = load_file_from_fixture(
            filename='test_tasks.json',
            add_paths=['tasks'],
        )['filter']

    def setUp(self):
        """Setup always when test executed."""
        self.client.login(**self.credentials)

    def get_absolute_filter_url(self, **kwargs) -> str:
        """
        Get absolute url use query string.

        Args:
            kwargs:

        Returns:
            str:
        """
        data = {'status': '', 'executor': '', 'label': ''}
        data.update(kwargs)
        query_str = '?status={status}&executor={executor}&label={label}'
        if 'creator' in kwargs:
            query_str = '{query_str}&self_tasks=on'.format(query_str=query_str)
        query_str = query_str.format(**data)
        return '{url}{query_str}'.format(url=self.url, query_str=query_str)

    def test_filters_by_each_field(self):
        """Test filters by each field."""
        mapping_fields_db = {
            'status': 'status',
            'executor': 'executor',
            'label': 'labels',
        }
        query_data = [
            ('status', self.data['status']),
            ('executor', self.data['executor']),
            ('label', self.data['label']),
        ]
        for data in query_data:
            field, field_data = data
            count_rec_in_db = self.model.objects.filter(
                **{mapping_fields_db[field]: field_data},
            ).count()
            response = self.client.get(
                self.get_absolute_filter_url(**{field: field_data}),
            )
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertEqual(count_rec_in_db, len(response.context['tasks_list']))

    def test_filter_switch_on_off_task_only_author(self):
        """Test switch on/off task only author."""
        data = {'creator': self.data['creator']}
        count_rec_switch_on = self.model.objects.filter(**data).count()
        response = self.client.get(self.get_absolute_filter_url(**data))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(count_rec_switch_on, len(response.context['tasks_list']))

        count_rec_switch_off = self.model.objects.all().count()
        response = self.client.get(self.get_absolute_filter_url())
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(count_rec_switch_off, len(response.context['tasks_list']))


class TestCreateViewCase(TestCase):
    """Test create view."""

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        cls.user_model = get_user_model()
        cls.status = Status.objects.create(name='test_status')
        cls.credentials = {'username': 'test', 'password': 'test'}
        cls.user = cls.user_model.objects.create_user(**cls.credentials)
        cls.data = {
            'name': 'test_task',
            'status': cls.status.pk,
            'creator': cls.user.pk,
            'executor': cls.user.pk,
        }

    def setUp(self):
        """Setup always when test executed."""
        self.client.login(**self.credentials)

    def test_create_view(self):
        """Test check view create model."""
        response = self.client.get(reverse('create_task'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'tasks/create.html')

        response = self.client.post(
            path=reverse('create_task'),
            data=self.data,
        )
        self.assertRedirects(response, reverse('tasks'))
        self.assertEqual(
            self.data['name'],
            Tasks.objects.get(name=self.data['name']).name,
        )

    def test_cannot_create(self):
        """Test check unique field."""
        response = self.client.post(
            path=reverse('create_task'),
            data=self.data,
        )
        self.assertRedirects(response, reverse('tasks'))
        count_tasks = Tasks.objects.all().count()

        response = self.client.post(
            path=reverse('create_task'),
            data=self.data,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(count_tasks, Tasks.objects.all().count())

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

    fixtures = [
        'tasks/db_users.json',
        'tasks/db_statuses.json',
        'tasks/db_labels.json',
        'tasks/db_tasks.json',
    ]

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        cls.user_model = get_user_model()
        cls.credentials = {'username': 'user_test1', 'password': '12345'}
        cls.data = load_file_from_fixture(
            filename='test_tasks.json',
            add_paths=['tasks'],
        )

    def setUp(self) -> None:
        """Setup always when test executed."""
        self.client.login(**self.credentials)
        self.task = Tasks.objects.get(
            name=self.data['task_author_id_1']['name'],
        )

    def test_update_view(self):
        """Test check view update model."""
        data = {
            'name': 'another_name',
            'executor': self.data['task_author_id_1']['executor'],
            'creator': self.data['task_author_id_1']['creator'],
            'status': self.data['task_author_id_1']['status'],
        }
        response = self.client.post(
            path=reverse('update_task', args=[self.task.pk]),
            data=data,
        )
        self.assertRedirects(response, reverse('tasks'))
        self.assertEqual(
            data['name'],
            Tasks.objects.get(pk=self.task.pk).name,
        )

    def test_cannot_update(self):
        """Test check unique field."""
        response = self.client.post(
            path=reverse('update_task', args=[self.task.pk]),
            data=self.data['task_author_id_2'],
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotEqual(
            self.data['task_author_id_2']['name'],
            Tasks.objects.get(pk=self.task.pk).name,
        )

    def test_get_not_auth_users_cannot_update(self):
        """Test GET not authenticated users cannot update."""
        self.client.logout()
        response = self.client.get(
            reverse('update_task', args=[self.task.pk]),
        )
        self.assertRedirects(response, reverse('login'))

    def test_post_not_auth_users_cannot_update(self):
        """Test not authenticated users cannot update."""
        self.client.logout()
        response = self.client.post(
            reverse('update_task', args=[self.task.pk]),
        )
        self.assertRedirects(response, reverse('login'))


class TestDeleteCase(TestCase):
    """Test delete view."""

    fixtures = [
        'tasks/db_users.json',
        'tasks/db_statuses.json',
        'tasks/db_labels.json',
        'tasks/db_tasks.json',
    ]

    @classmethod
    def setUpTestData(cls):
        """Setup once test data."""
        cls.user_model = get_user_model()
        cls.credentials = {'username': 'user_test1', 'password': '12345'}
        cls.data = load_file_from_fixture(
            filename='test_tasks.json',
            add_paths=['tasks'],
        )

    def setUp(self) -> None:
        """Setup always when test executed."""
        self.client.login(**self.credentials)
        self.task = Tasks.objects.get(
            name=self.data['task_author_id_1']['name'],
        )

    def test_delete_view(self):
        """Test check view delete model."""
        response = self.client.post(
            path=reverse('delete_task', args=[self.task.pk]),
        )
        self.assertRedirects(response, reverse('tasks'))
        self.assertFalse(
            Tasks.objects.filter(
                name=self.data['task_author_id_1']['name'],
            ).exists()  # noqa: C812
        )

    def test_get_not_auth_users_cannot_delete(self):
        """Test GET not authenticated users cannot delete."""
        self.client.logout()
        response = self.client.get(
            reverse('delete_task', args=[self.task.pk]),
        )
        self.assertRedirects(response, reverse('login'))

    def test_post_not_auth_users_cannot_delete(self):
        """Test POST not authenticated users cannot delete."""
        self.client.logout()
        response = self.client.post(
            reverse('delete_task', args=[self.task.pk]),
        )
        self.assertRedirects(response, reverse('login'))

    def test_only_the_author_can_delete(self):
        """Test only the author task can delete."""
        task_another_author = Tasks.objects.get(
            name=self.data['task_author_id_2']['name'],
        )
        response = self.client.post(
            reverse('delete_task', args=[task_another_author.pk]),
        )
        self.assertRedirects(response, reverse('tasks'))
        self.assertNotEqual(
            task_another_author.creator,
            self.task.creator,
        )
        self.assertTrue(
            Tasks.objects.filter(
                name=self.data['task_author_id_2']['name'],
            ).exists()  # noqa: C812
        )
