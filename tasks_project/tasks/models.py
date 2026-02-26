from django.db import models
from django.urls import reverse

class ChatMessage(models.Model):
    SENDER_CHOICES = [
        ('user', 'User'),
        ('agent', 'Agent'),
    ]
    
    content = models.TextField()
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.get_sender_display()}: {self.content[:50]}"

class Project(models.Model):
    CATEGORY_CHOICES = [
        ('safety', 'Safety'),
        ('operational', 'Operational'),
        ('workshop', 'Workshop'),
        ('general', 'General'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#6c757d', help_text='Hex color code')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('project_detail', kwargs={'pk': self.pk})

class Task(models.Model):
    STATUS_CHOICES = [
        ('backlog', 'Backlog'),
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'Review'),
        ('done', 'Done'),
    ]
    
    PRIORITY_CHOICES = [
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
        (4, 'Urgent'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='backlog')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks', null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    tags = models.CharField(max_length=200, blank=True, help_text='Comma-separated tags')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-priority', 'due_date', 'created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('task_detail', kwargs={'pk': self.pk})
    
    def get_tags_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    @property
    def priority_class(self):
        return {
            1: 'bg-success',
            2: 'bg-info',
            3: 'bg-warning',
            4: 'bg-danger',
        }.get(self.priority, 'bg-secondary')
    
    @property
    def priority_label(self):
        return dict(self.PRIORITY_CHOICES).get(self.priority, 'Medium')


class Incident(models.Model):
    SEVERITY_CHOICES = [
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date_reported = models.DateField(auto_now_add=True)
    severity = models.IntegerField(choices=SEVERITY_CHOICES, default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    action_taken = models.TextField(blank=True, help_text='Actions taken or planned')
    closed_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_reported', '-severity']
    
    def __str__(self):
        return f"{self.title} ({self.get_severity_display()} - {self.get_status_display()})"
    
    def get_absolute_url(self):
        return reverse('incident_detail', kwargs={'pk': self.pk})
    
    @property
    def severity_class(self):
        return {
            1: 'bg-info',
            2: 'bg-warning',
            3: 'bg-danger',
        }.get(self.severity, 'bg-secondary')
