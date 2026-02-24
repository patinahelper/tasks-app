from django.urls import path
from . import views
from . import api

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('chat/', views.chat_view, name='chat'),
    path('chat/api/', views.chat_api, name='chat_api'),
    path('chat/poll/', views.chat_poll, name='chat_poll'),
    path('kanban/', views.kanban_board, name='kanban'),
    path('task/move/', views.task_move, name='task_move'),
    path('tasks/', views.TaskListView.as_view(), name='task_list'),
    path('task/new/', views.TaskCreateView.as_view(), name='task_create'),
    path('task/<int:pk>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('task/<int:pk>/edit/', views.TaskUpdateView.as_view(), name='task_update'),
    path('task/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),
    path('projects/', views.ProjectListView.as_view(), name='project_list'),
    path('project/new/', views.ProjectCreateView.as_view(), name='project_create'),
    path('project/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('project/<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='project_update'),
    
    # API endpoints
    path('api/tasks/', api.list_tasks, name='api_task_list'),
    path('api/tasks/create/', api.create_task, name='api_task_create'),
    path('api/tasks/search/', api.search_tasks, name='api_task_search'),
    path('api/tasks/<int:pk>/', api.get_task, name='api_task_detail'),
    path('api/tasks/<int:pk>/update/', api.update_task, name='api_task_update'),
    path('api/tasks/<int:pk>/delete/', api.delete_task, name='api_task_delete'),
    path('api/tasks/<int:pk>/move/', api.move_task, name='api_task_move'),
    path('api/projects/', api.list_projects, name='api_project_list'),
    path('api/projects/create/', api.create_project, name='api_project_create'),
]
