"""
URL configuration for tasks_project project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tasks_project.tasks.urls')),
]
