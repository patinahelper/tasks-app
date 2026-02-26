#!/usr/bin/env python3
"""
Tasks App Helper - Direct database access for Telegram commands.

Usage:
    from tasks_helper import list_projects, add_task, update_task, etc.
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django - must add project dir to path BEFORE importing
project_path = '/data/workspace/tasks-app/tasks_project'
if project_path not in sys.path:
    sys.path.insert(0, project_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tasks_project.settings')
django.setup()

# Import after django.setup() - use full app path
from tasks_project.tasks.models import Project, Task, ChatMessage, Incident


def list_projects():
    """Return list of active projects."""
    projects = Project.objects.filter(is_active=True).order_by('-updated_at')
    return [(p.id, p.name, p.color) for p in projects]


def get_project(name_or_id):
    """Get project by name (partial match) or ID."""
    try:
        # Try ID first
        return Project.objects.get(id=int(name_or_id), is_active=True)
    except (ValueError, Project.DoesNotExist):
        # Try name match
        projects = Project.objects.filter(name__icontains=name_or_id, is_active=True)
        if projects.exists():
            return projects.first()
    return None


def list_tasks(project_name=None, status=None, priority=None, limit=20):
    """Return list of tasks with optional filters."""
    qs = Task.objects.all()
    
    if project_name:
        project = get_project(project_name)
        if project:
            qs = qs.filter(project=project)
    
    if status:
        qs = qs.filter(status=status)
    
    if priority:
        qs = qs.filter(priority=priority)
    
    qs = qs.order_by('-priority', 'due_date', '-created_at')[:limit]
    
    return [(t.id, t.title, t.get_status_display(), t.priority_label, 
             str(t.due_date) if t.due_date else None, 
             t.project.name if t.project else "No project") for t in qs]


def get_task(task_id_or_title):
    """Get task by ID or partial title match."""
    try:
        return Task.objects.get(id=int(task_id_or_title))
    except (ValueError, Task.DoesNotExist):
        tasks = Task.objects.filter(title__icontains=task_id_or_title)
        if tasks.exists():
            return tasks.first()
    return None


def add_task(title, project_name=None, description="", status="backlog", 
             priority=2, due_date=None, tags=""):
    """
    Add a new task.
    
    Args:
        title: Task title
        project_name: Project name (will be matched or created if not found)
        description: Task description
        status: One of: backlog, todo, in_progress, review, done
        priority: 1=Low, 2=Medium, 3=High, 4=Urgent
        due_date: Date string (YYYY-MM-DD) or None
        tags: Comma-separated tags
    """
    project = None
    if project_name:
        project = get_project(project_name)
        if not project:
            # Create project with default color
            project = Project.objects.create(
                name=project_name,
                description=f"Created via Telegram",
                color="#6c757d"
            )
    
    # Parse due_date if string
    if isinstance(due_date, str):
        try:
            due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
        except ValueError:
            due_date = None
    
    task = Task.objects.create(
        title=title,
        project=project,
        description=description,
        status=status,
        priority=priority,
        due_date=due_date,
        tags=tags
    )
    
    return task


def add_project(name, description="", color="#6c757d"):
    """Create a new project."""
    project = Project.objects.create(
        name=name,
        description=description,
        color=color
    )
    return project


def update_task(task_id_or_title, **kwargs):
    """
    Update a task.
    
    Args:
        task_id_or_title: Task ID or title to find
        **kwargs: Fields to update (title, description, status, priority, due_date, tags)
    """
    task = get_task(task_id_or_title)
    if not task:
        return None
    
    # Handle special fields
    if 'project' in kwargs:
        project = get_project(kwargs.pop('project'))
        if project:
            task.project = project
    
    if 'due_date' in kwargs and isinstance(kwargs['due_date'], str):
        try:
            kwargs['due_date'] = datetime.strptime(kwargs['due_date'], '%Y-%m-%d').date()
        except ValueError:
            del kwargs['due_date']
    
    # Handle status shortcuts
    if 'status' in kwargs:
        status_map = {
            'done': 'done',
            'complete': 'done',
            'completed': 'done',
            'finish': 'done',
            'finished': 'done',
            'todo': 'todo',
            'to do': 'todo',
            'backlog': 'backlog',
            'in progress': 'in_progress',
            'inprogress': 'in_progress',
            'doing': 'in_progress',
            'review': 'review',
        }
        kwargs['status'] = status_map.get(kwargs['status'].lower(), kwargs['status'])
        
        # Set completed_at if marking done
        if kwargs['status'] == 'done' and not task.completed_at:
            kwargs['completed_at'] = datetime.now()
    
    # Handle priority shortcuts
    if 'priority' in kwargs:
        priority_map = {
            'low': 1, '1': 1,
            'medium': 2, 'med': 2, '2': 2,
            'high': 3, '3': 3,
            'urgent': 4, 'urg': 4, '4': 4,
        }
        if isinstance(kwargs['priority'], str):
            kwargs['priority'] = priority_map.get(kwargs['priority'].lower(), 2)
    
    # Update fields
    for key, value in kwargs.items():
        if hasattr(task, key):
            setattr(task, key, value)
    
    task.save()
    return task


def delete_task(task_id_or_title):
    """Delete a task."""
    task = get_task(task_id_or_title)
    if task:
        task.delete()
        return True
    return False


def get_urgent_tasks():
    """Get all urgent priority tasks not done."""
    return list_tasks(priority=4)


def get_tasks_due_soon(days=3):
    """Get tasks due within N days."""
    cutoff = datetime.now().date() + timedelta(days=days)
    tasks = Task.objects.filter(
        due_date__lte=cutoff,
        due_date__isnull=False,
        status__in=['backlog', 'todo', 'in_progress', 'review']
    ).order_by('due_date')
    
    return [(t.id, t.title, str(t.due_date), t.project.name if t.project else "No project") 
            for t in tasks]


def format_task_list(tasks, title="Tasks"):
    """Format task list for display."""
    if not tasks:
        return f"No {title.lower()}."
    
    lines = [f"**{title}:**"]
    for t in tasks:
        task_id, title, status, priority, due, project = t
        due_str = f" (due {due})" if due else ""
        lines.append(f"• {title} — {priority}{due_str}")
    return "\n".join(lines)


# ========== Incident Functions ==========

def list_incidents(status=None, severity=None, limit=20):
    """Return list of incidents with optional filters."""
    qs = Incident.objects.all()
    
    if status:
        qs = qs.filter(status=status)
    
    if severity:
        qs = qs.filter(severity=severity)
    
    qs = qs.order_by('-date_reported', '-severity')[:limit]
    
    return [(i.id, i.title, i.get_severity_display(), i.get_status_display(), 
             str(i.date_reported)) for i in qs]


def get_incident(incident_id_or_title):
    """Get incident by ID or partial title match."""
    try:
        return Incident.objects.get(id=int(incident_id_or_title))
    except (ValueError, Incident.DoesNotExist):
        incidents = Incident.objects.filter(title__icontains=incident_id_or_title)
        if incidents.exists():
            return incidents.first()
    return None


def add_incident(title, description="", severity=2, action_taken=""):
    """
    Add a new incident/hazard report.
    
    Args:
        title: Incident title
        description: What happened
        severity: 1=Low, 2=Medium, 3=High
        action_taken: Actions taken or planned
    """
    # Handle severity shortcuts
    severity_map = {
        'low': 1, '1': 1,
        'medium': 2, 'med': 2, '2': 2,
        'high': 3, '3': 3,
    }
    if isinstance(severity, str):
        severity = severity_map.get(severity.lower(), 2)
    
    incident = Incident.objects.create(
        title=title,
        description=description,
        severity=severity,
        action_taken=action_taken,
        status='open'
    )
    
    return incident


def update_incident(incident_id_or_title, **kwargs):
    """
    Update an incident.
    
    Args:
        incident_id_or_title: Incident ID or title to find
        **kwargs: Fields to update (title, description, severity, status, action_taken, closed_at)
    """
    incident = get_incident(incident_id_or_title)
    if not incident:
        return None
    
    # Handle severity shortcuts
    if 'severity' in kwargs and isinstance(kwargs['severity'], str):
        severity_map = {
            'low': 1, '1': 1,
            'medium': 2, 'med': 2, '2': 2,
            'high': 3, '3': 3,
        }
        kwargs['severity'] = severity_map.get(kwargs['severity'].lower(), 2)
    
    # Handle status shortcuts
    if 'status' in kwargs:
        status_map = {
            'open': 'open',
            'in progress': 'in_progress',
            'inprogress': 'in_progress',
            'closed': 'closed',
            'close': 'closed',
            'resolved': 'closed',
        }
        if isinstance(kwargs['status'], str):
            kwargs['status'] = status_map.get(kwargs['status'].lower(), kwargs['status'])
        
        # Set closed_at if marking closed
        if kwargs['status'] == 'closed' and not incident.closed_at:
            kwargs['closed_at'] = datetime.now().date()
    
    # Update fields
    for key, value in kwargs.items():
        if hasattr(incident, key):
            setattr(incident, key, value)
    
    incident.save()
    return incident


def close_incident(incident_id_or_title, action_taken=None):
    """Close an incident with optional action note."""
    incident = get_incident(incident_id_or_title)
    if not incident:
        return None
    
    incident.status = 'closed'
    incident.closed_at = datetime.now().date()
    if action_taken:
        incident.action_taken = action_taken
    incident.save()
    return incident


def get_open_incidents():
    """Get all open incidents."""
    return list_incidents(status__in=['open', 'in_progress'])


# ========== Weekly Report Helper ==========

def get_weekly_report(days=7):
    """
    Get data for weekly report.
    
    Returns dict with:
    - completed_tasks
    - in_progress_tasks  
    - upcoming_tasks
    - new_incidents
    - open_incidents
    """
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    completed_tasks = Task.objects.filter(
        completed_at__date__gte=start_date,
        completed_at__date__lte=end_date
    ).select_related('project').order_by('project__category', '-completed_at')
    
    in_progress_tasks = Task.objects.filter(
        status='in_progress'
    ).select_related('project').order_by('project__category', '-priority')
    
    upcoming_tasks = Task.objects.filter(
        due_date__gte=end_date,
        due_date__lte=end_date + timedelta(days=7),
        status__in=['backlog', 'todo', 'in_progress']
    ).select_related('project').order_by('due_date')
    
    new_incidents = Incident.objects.filter(
        date_reported__gte=start_date,
        date_reported__lte=end_date
    ).order_by('-severity', '-date_reported')
    
    open_incidents = Incident.objects.filter(
        status__in=['open', 'in_progress']
    ).order_by('-severity', '-date_reported')
    
    return {
        'start_date': start_date,
        'end_date': end_date,
        'completed_tasks': completed_tasks,
        'in_progress_tasks': in_progress_tasks,
        'upcoming_tasks': upcoming_tasks,
        'new_incidents': new_incidents,
        'open_incidents': open_incidents,
    }


if __name__ == "__main__":
    # Quick test
    print("Projects:")
    for p in list_projects():
        print(f"  {p[0]}: {p[1]}")
    
    print("\nRecent tasks:")
    for t in list_tasks(limit=5):
        print(f"  {t[0]}: {t[1]} ({t[2]})")
    
    print("\nOpen incidents:")
    for i in list_incidents(status='open'):
        print(f"  {i[0]}: {i[1]} ({i[2]} - {i[3]})")
