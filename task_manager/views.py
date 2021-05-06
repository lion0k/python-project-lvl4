"""Task manager views."""
from django.views.generic.base import TemplateView


class HomePageView(TemplateView):
    """Home page view."""

    template_name = 'index.html'
