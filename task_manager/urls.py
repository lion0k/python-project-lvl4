"""task_manager URL Configuration."""
from django.contrib import admin
from django.urls import include, path
from task_manager import views
from task_manager.users.views import UserLoginView, UserLogoutView

urlpatterns = [
    path('', views.index, name='home'),
    path('admin/', admin.site.urls),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('users/', include('task_manager.users.urls')),
    path('statuses/', include('task_manager.statuses.urls')),
]
