"""task_manager URL Configuration."""
from django.contrib import admin
from django.urls import include, path
from task_manager import views

urlpatterns = [
    path('', views.index, name='home'),
    path('admin/', admin.site.urls),
    path('users/', include('task_manager.users.urls')),
]
