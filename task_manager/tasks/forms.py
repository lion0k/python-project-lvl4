"""Task forms."""
from django import forms
from task_manager.tasks.models import Tasks


class TasksForm(forms.ModelForm):
    """Task form."""

    class Meta(object):
        """Meta information."""

        model = Tasks
        fields = ['name', 'description', 'status', 'executor', 'labels']
