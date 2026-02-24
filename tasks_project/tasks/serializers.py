from rest_framework import serializers
from .models import Project, Task

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'color', 'is_active', 'created_at', 'updated_at']

class TaskSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    priority_label = serializers.CharField(source='get_priority_display', read_only=True)
    status_label = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'status_label', 
            'priority', 'priority_label', 'project', 'project_name',
            'due_date', 'tags', 'created_at', 'updated_at', 'completed_at'
        ]
