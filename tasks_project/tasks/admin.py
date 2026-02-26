from django.contrib import admin
from .models import Project, Task, ChatMessage, Incident

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'content_preview', 'timestamp', 'is_read']
    list_filter = ['sender', 'is_read']
    readonly_fields = ['timestamp']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_active', 'created_at', 'updated_at']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'priority_label', 'project', 'due_date', 'updated_at']
    list_filter = ['status', 'priority', 'project__category', 'project']
    search_fields = ['title', 'description', 'tags']
    date_hierarchy = 'due_date'

@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ['title', 'severity_label', 'status', 'date_reported', 'updated_at']
    list_filter = ['severity', 'status', 'date_reported']
    search_fields = ['title', 'description', 'action_taken']
    date_hierarchy = 'date_reported'
    
    def severity_label(self, obj):
        return obj.get_severity_display()
    severity_label.short_description = 'Severity'
