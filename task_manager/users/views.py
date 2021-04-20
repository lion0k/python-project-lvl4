"""User views."""
from typing import Any

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from task_manager.users.forms import CustomUserCreationForm
from task_manager.users.mixins import CheckUserRightsTestMixin


class UserListView(ListView):
    """User listing."""

    model = get_user_model()
    paginate_by = 10
    context_object_name = 'users_list'
    template_name = 'users/index.html'

    def listing(self, request) -> HttpResponse:
        """
        Get all users.

        Args:
            request:

        Returns:
            HttpResponse:
        """
        users_list = get_user_model().objects.all()
        paginator = Paginator(users_list, per_page=10)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, self.template_name, {'page_obj': page_obj})


class UserCreateView(SuccessMessageMixin, CreateView):
    """User create form."""

    form_class = CustomUserCreationForm
    template_name = 'users/create.html'
    success_message = _('SuccessCreateUser')
    success_url = reverse_lazy('users')


class UserUpdateView(
    CheckUserRightsTestMixin,
    SuccessMessageMixin,
    UpdateView,
):
    """User update form."""

    model = get_user_model()
    form_class = CustomUserCreationForm
    template_name = 'users/update.html'
    success_url = reverse_lazy('users')
    success_message = _('SuccessUpdateUser')


class UserDeleteView(
    CheckUserRightsTestMixin,
    SuccessMessageMixin,
    DeleteView,
):
    """User delete form."""

    model = get_user_model()
    template_name = 'users/delete.html'
    success_url = reverse_lazy('users')
    success_message = _('SuccessDeleteUser')


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
