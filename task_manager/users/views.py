from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.generic.list import ListView

from .models import CustomUser


class UserListView(ListView):
    model = CustomUser
    paginate_by = 2
    context_object_name = 'users_list'
    template_name = 'users/index.html'

    def listing(self, request):
        users_list = CustomUser.objects.all()
        paginator = Paginator(users_list, 2)

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, self.template_name, {'page_obj': page_obj})
