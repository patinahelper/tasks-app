from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
import json
from .models import Project, Task, ChatMessage
from .forms import TaskForm, ProjectForm, ChatMessageForm

def chat_view(request):
    """Chat interface with BMO"""
    if request.method == 'POST':
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = 'user'
            message.save()
            return redirect('chat')
    else:
        form = ChatMessageForm()
    
    # Get recent messages (last 50) - ordered by timestamp
    messages = ChatMessage.objects.order_by('-timestamp')[:50]
    # Reverse so oldest first for display
    messages = list(reversed(messages))
    
    # Get last message ID for polling
    last_message_id = messages[-1].id if messages else 0
    
    context = {
        'messages': messages,
        'form': form,
        'unread_count': ChatMessage.objects.filter(sender='agent', is_read=False).count(),
        'last_message_id': last_message_id,
    }
    return render(request, 'tasks/chat.html', context)

@require_POST
def chat_api(request):
    """AJAX endpoint to send message"""
    data = json.loads(request.body)
    content = data.get('message', '').strip()
    
    if content:
        ChatMessage.objects.create(
            content=content,
            sender='user',
            timestamp=timezone.now()
        )
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Empty message'})

def chat_poll(request):
    """AJAX endpoint to poll for new messages"""
    last_id = request.GET.get('last_id')
    
    if last_id:
        messages = ChatMessage.objects.filter(id__gt=last_id).values('id', 'content', 'sender', 'timestamp')
    else:
        messages = ChatMessage.objects.all().values('id', 'content', 'sender', 'timestamp')
    
    # Mark agent messages as read
    ChatMessage.objects.filter(sender='agent', is_read=False).update(is_read=True)
    
    return JsonResponse({
        'messages': list(messages),
        'unread_count': ChatMessage.objects.filter(sender='agent', is_read=False).count(),
    })

def dashboard(request):
    """Main dashboard view"""
    context = {
        'total_tasks': Task.objects.count(),
        'tasks_by_status': {
            'backlog': Task.objects.filter(status='backlog').count(),
            'todo': Task.objects.filter(status='todo').count(),
            'in_progress': Task.objects.filter(status='in_progress').count(),
            'review': Task.objects.filter(status='review').count(),
            'done': Task.objects.filter(status='done').count(),
        },
        'urgent_tasks': Task.objects.filter(priority=4, status__in=['backlog', 'todo', 'in_progress']).order_by('due_date')[:5],
        'recent_tasks': Task.objects.order_by('-updated_at')[:10],
        'projects': Project.objects.filter(is_active=True),
    }
    return render(request, 'tasks/dashboard.html', context)

def kanban_board(request):
    """Kanban board view"""
    project_id = request.GET.get('project')
    tasks = Task.objects.all()
    
    if project_id:
        tasks = tasks.filter(project_id=project_id)
    
    context = {
        'columns': [
            {'id': 'backlog', 'name': 'Backlog', 'tasks': tasks.filter(status='backlog')},
            {'id': 'todo', 'name': 'To Do', 'tasks': tasks.filter(status='todo')},
            {'id': 'in_progress', 'name': 'In Progress', 'tasks': tasks.filter(status='in_progress')},
            {'id': 'review', 'name': 'Review', 'tasks': tasks.filter(status='review')},
            {'id': 'done', 'name': 'Done', 'tasks': tasks.filter(status='done')},
        ],
        'projects': Project.objects.filter(is_active=True),
        'current_project': int(project_id) if project_id else None,
    }
    return render(request, 'tasks/kanban.html', context)

@require_POST
def task_move(request):
    """AJAX endpoint to move task between columns"""
    data = json.loads(request.body)
    task_id = data.get('task_id')
    new_status = data.get('status')
    
    task = get_object_or_404(Task, pk=task_id)
    task.status = new_status
    if new_status == 'done':
        from django.utils import timezone
        task.completed_at = timezone.now()
    task.save()
    
    return JsonResponse({'success': True})

class ProjectListView(ListView):
    model = Project
    template_name = 'tasks/project_list.html'
    context_object_name = 'projects'

class ProjectDetailView(DetailView):
    model = Project
    template_name = 'tasks/project_detail.html'
    
    def get_context_data(self, **kwargs):
        from django.utils import timezone
        context = super().get_context_data(**kwargs)
        context['tasks'] = self.object.tasks.order_by('-priority', 'due_date')
        context['today'] = timezone.now().date()
        # Task counts for stats
        context['total_tasks'] = self.object.tasks.count()
        context['in_progress_count'] = self.object.tasks.filter(status='in_progress').count()
        context['completed_count'] = self.object.tasks.filter(status='done').count()
        return context

class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'tasks/project_form.html'
    success_url = reverse_lazy('project_list')

class ProjectUpdateView(UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'tasks/project_form.html'
    success_url = reverse_lazy('project_list')

class TaskListView(ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 20

    def get_queryset(self):
        from django.utils import timezone
        from datetime import timedelta
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        project = self.request.GET.get('project')
        priority = self.request.GET.get('priority')
        due = self.request.GET.get('due')

        if status:
            queryset = queryset.filter(status=status)
        if project:
            queryset = queryset.filter(project_id=project)
        if priority:
            queryset = queryset.filter(priority=priority)

        # Due date filters
        today = timezone.now().date()
        if due == 'today':
            queryset = queryset.filter(due_date=today)
        elif due == 'week':
            week_end = today + timedelta(days=7)
            queryset = queryset.filter(due_date__gte=today, due_date__lte=week_end)
        elif due == 'overdue':
            queryset = queryset.filter(due_date__lt=today, status__in=['backlog', 'todo', 'in_progress'])

        return queryset

    def get_context_data(self, **kwargs):
        from django.utils import timezone
        from datetime import timedelta
        context = super().get_context_data(**kwargs)
        context['projects'] = Project.objects.filter(is_active=True)
        context['status_choices'] = Task.STATUS_CHOICES
        context['priority_choices'] = Task.PRIORITY_CHOICES
        context['today'] = timezone.now().date()
        context['week_end'] = timezone.now().date() + timedelta(days=7)

        # Due date counts for filter badges
        today = timezone.now().date()
        week_end = today + timedelta(days=7)
        base_qs = Task.objects.exclude(status='done')
        context['due_today_count'] = base_qs.filter(due_date=today).count()
        context['due_this_week_count'] = base_qs.filter(due_date__gte=today, due_date__lte=week_end).count()
        context['overdue_count'] = base_qs.filter(due_date__lt=today).count()

        # Current filter
        context['current_due'] = self.request.GET.get('due', '')
        return context

class TaskDetailView(DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'

class TaskCreateView(CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('kanban')

class TaskUpdateView(UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    
    def get_success_url(self):
        return reverse_lazy('task_detail', kwargs={'pk': self.object.pk})

class TaskDeleteView(DeleteView):
    model = Task
    success_url = reverse_lazy('kanban')
    template_name = 'tasks/task_confirm_delete.html'
