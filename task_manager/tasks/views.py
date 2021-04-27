"""Tasks views."""
from typing import Any

from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from task_manager.tasks.forms import TasksForm
from task_manager.tasks.mixins import (
    CheckUserRightsTestMixin,
    CustomLoginRequiredMixin,
)
from task_manager.tasks.models import Tasks


class TaskListView(CustomLoginRequiredMixin, ListView):
    """Task listing."""

    model = Tasks
    paginate_by = 10
    queryset = model.objects.prefetch_related('status', 'executor', 'creator')
    login_url = reverse_lazy('login')
    context_object_name = 'tasks_list'
    template_name = 'tasks/index.html'


class TaskCreateView(
    CustomLoginRequiredMixin,
    SuccessMessageMixin,
    CreateView,
):
    """Task create."""

    model = Tasks
    form_class = TasksForm
    queryset = model.objects.prefetch_related('status', 'executor', 'creator')
    login_url = reverse_lazy('login')
    template_name = 'tasks/create.html'
    success_message = _('SuccessCreateTask')
    success_url = reverse_lazy('tasks')

    def form_valid(self, form) -> Any:
        """
        If the form is valid, save the associated model.

        Args:
            form:

        Returns:
            Any:
        """
        form.instance.creator = self.request.user
        return super().form_valid(form)


class TaskUpdateView(
    CustomLoginRequiredMixin,
    SuccessMessageMixin,
    UpdateView,
):
    """Task update."""

    model = Tasks
    form_class = TasksForm
    queryset = model.objects.prefetch_related('status', 'executor', 'creator')
    login_url = reverse_lazy('login')
    template_name = 'tasks/update.html'
    success_url = reverse_lazy('tasks')
    success_message = _('SuccessUpdateTask')


class TaskDeleteView(
    CheckUserRightsTestMixin,
    SuccessMessageMixin,
    DeleteView,
):
    """Task delete."""

    model = Tasks
    template_name = 'tasks/delete.html'
    success_url = reverse_lazy('tasks')
    success_message = _('SuccessDeleteTask')
    redirect_url = reverse_lazy('tasks')

    def test_func(self) -> bool:
        """
        Test function.

        Returns:
            bool:
        """
        return self.get_object().creator == self.request.user