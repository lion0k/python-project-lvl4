"""Task manager views."""
from django.http import HttpResponse
from django.shortcuts import render


def index(request) -> HttpResponse:
    """
    Test.

    Args:
        request: request

    Returns:
        HttpResponse:
    """
    return render(request, 'index.html')
