"""Status model."""
from django.db import models
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


class Status(models.Model):
    """Status model."""

    name = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name=_('StatusName'),
        help_text=_('HelpStatusFieldText'),
        error_messages={
            'unique': _('StatusWithThisNameAlreadyExist'),
            'blank': _('ThisFieldCannotBeBlank'),
        },
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """
        String representation.

        Returns:
            str:
        """
        return self.name

    def get_absolute_url(self):  # noqa: D102
        return reverse_lazy('statuses')

    class Meta(object):
        """Meta information."""

        verbose_name = _('Status')
        verbose_name_plural = _('Statuses')
        ordering = ['name']
