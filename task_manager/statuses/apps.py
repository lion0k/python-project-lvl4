"""Statuses application."""
from django.apps import AppConfig


class StatusesConfig(AppConfig):
    """Config status."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'task_manager.statuses'
