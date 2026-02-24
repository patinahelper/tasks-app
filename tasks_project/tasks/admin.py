from django.contrib import admin
from .models import Project, Task, ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'content_preview', 'timestamp', 'is_read']
    list_filter = ['sender', 'is_read']
    readonly_fields = ['timestamp']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'priority_label', 'project', 'due_date', 'updated_at']
    list_filter = ['status', 'priority', 'project']
    search_fields = ['title', 'description', 'tags']
    date_hierarchy = 'due_date'
