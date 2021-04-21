"""task_manager URL Configuration."""
from django.contrib import admin
from django.urls import include, path
from task_manager.users.views import UserLoginView, UserLogoutView
from task_manager import views

urlpatterns = [
    path('', views.index, name='home'),
    path('admin/', admin.site.urls),
    path('users/', include('task_manager.users.urls')),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
]
