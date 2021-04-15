from django.shortcuts import render
from django.utils.translation import gettext as _


def index(request):
    return render(request, 'base.html', context={
        'hello': _('Hello'),
    })