"""User views."""
from typing import Any

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models.deletion import ProtectedError
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from task_manager.mixins import CustomLoginRequiredMixin
from task_manager.users.forms import CustomUserCreationForm
from task_manager.users.mixins import UserIsHimselfMixin


class UserListView(ListView):
    """User listing."""

    model = get_user_model()
    paginate_by = 10
    context_object_name = 'users_list'
    template_name = 'users/index.html'


class UserDetailView(CustomLoginRequiredMixin, DetailView):
    """User detail view."""

    model = get_user_model()
    context_object_name = 'user'
    template_name = 'users/detail.html'


class UserCreateView(SuccessMessageMixin, CreateView):
    """User create."""

    model = get_user_model()
    form_class = CustomUserCreationForm
    template_name = 'users/create.html'
    success_message = _('SuccessCreateUser')
    success_url = reverse_lazy('login')


class UserUpdateView(
    CustomLoginRequiredMixin,
    UserIsHimselfMixin,
    SuccessMessageMixin,
    UpdateView,
):
    """User update."""

    model = get_user_model()
    context_object_name = 'user'
    form_class = CustomUserCreationForm
    template_name = 'users/update.html'
    success_message = _('SuccessUpdateUser')
    error_message = _('ErrorUserNotHaveRights')
    redirect_url = reverse_lazy('users')


class UserDeleteView(
    CustomLoginRequiredMixin,
    UserIsHimselfMixin,
    SuccessMessageMixin,
    DeleteView,
):
    """User delete."""

    model = get_user_model()
    context_object_name = 'user'
    template_name = 'users/delete.html'
    success_url = reverse_lazy('users')
    success_message = _('SuccessDeleteUser')
    error_message = _('ErrorUserNotHaveRights')
    redirect_url = reverse_lazy('users')

    def post(self, request, *args, **kwargs) -> HttpResponseRedirect:
        """
        Override 'post' in DeletionMixin.

        Args:
            request: request

        Returns:
            Union:
        """
        try:
            response = self.delete(request, *args, **kwargs)
            messages.success(self.request, self.success_message)
            return response
        except ProtectedError:
            messages.error(self.request, _('CannotDeleteUser'))
            return redirect('users')


class UserLoginView(SuccessMessageMixin, LoginView):
    """User login."""

    template_name = 'users/login.html'
    success_message = _('SuccessLoginUser')


class UserLogoutView(LogoutView):
    """User logout."""

    def dispatch(self, request, *args, **kwargs) -> Any:
        """
        Dispatch.

        Args:
            request:

        Returns:
            Any:
        """
        if request.user.is_authenticated:
            messages.success(request, _('SuccessLogoutUser'))
        return super().dispatch(request, *args, **kwargs)
