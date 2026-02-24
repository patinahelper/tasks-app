from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from .models import Project, Task
from .serializers import ProjectSerializer, TaskSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    
    def perform_update(self, serializer):
        # Auto-set completed_at when status changes to done
        if serializer.validated_data.get('status') == 'done':
            serializer.save(completed_at=timezone.now())
        else:
            serializer.save()

# Simple API endpoints for agent use
@api_view(['POST'])
def create_task(request):
    """Create a new task"""
    serializer = TaskSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def list_tasks(request):
    """List all tasks with optional filtering"""
    queryset = Task.objects.all()
    
    # Filter by status
    status_filter = request.query_params.get('status')
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    
    # Filter by project
    project_filter = request.query_params.get('project')
    if project_filter:
        queryset = queryset.filter(project_id=project_filter)
    
    # Filter by priority
    priority_filter = request.query_params.get('priority')
    if priority_filter:
        queryset = queryset.filter(priority=priority_filter)
    
    serializer = TaskSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_task(request, pk):
    """Get a specific task"""
    try:
        task = Task.objects.get(pk=pk)
        serializer = TaskSerializer(task)
        return Response(serializer.data)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PATCH'])
def update_task(request, pk):
    """Update a task"""
    try:
        task = Task.objects.get(pk=pk)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            # Auto-set completed_at when status changes to done
            if request.data.get('status') == 'done':
                serializer.save(completed_at=timezone.now())
            else:
                serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
def delete_task(request, pk):
    """Delete a task"""
    try:
        task = Task.objects.get(pk=pk)
        task.delete()
        return Response({'message': 'Task deleted successfully'})
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def create_project(request):
    """Create a new project"""
    serializer = ProjectSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def list_projects(request):
    """List all projects"""
    queryset = Project.objects.filter(is_active=True)
    serializer = ProjectSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def move_task(request, pk):
    """Move a task to a different status (kanban)"""
    try:
        task = Task.objects.get(pk=pk)
        new_status = request.data.get('status')
        if new_status not in ['backlog', 'todo', 'in_progress', 'review', 'done']:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        task.status = new_status
        if new_status == 'done':
            task.completed_at = timezone.now()
        task.save()
        
        serializer = TaskSerializer(task)
        return Response(serializer.data)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def search_tasks(request):
    """Search tasks by title or description"""
    query = request.query_params.get('q', '')
    tasks = Task.objects.filter(title__icontains=query) | Task.objects.filter(description__icontains=query)
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)
