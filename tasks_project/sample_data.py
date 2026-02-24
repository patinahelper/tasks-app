# Sample data to load after migrations
# Run: python manage.py shell < sample_data.py

from tasks_project.tasks.models import Project, Task
from django.utils import timezone

# Create Mavin Lab Project
mavin, created = Project.objects.get_or_create(
    name='Mavin Lab Project',
    defaults={
        'description': 'Client project for Mavin Lab — reviewing initial design and equipment pricing for copper oxide, vanadium, and mine tailings processing lab and pilot plant.',
        'color': '#0d6efd',
        'is_active': True
    }
)

if created:
    print(f"Created project: {mavin.name}")
    
    # Create sample tasks
    tasks = [
        {
            'title': 'Review Sample Prep equipment list',
            'description': 'Check initial equipment list for crushing, splitting, sizing, and storage. Add LIMS and sample station requirements.',
            'status': 'todo',
            'priority': 3,
        },
        {
            'title': 'Review Comminution equipment',
            'description': 'Evaluate grinding mills, particle size analysis equipment, liberation study setups for both research lab and pilot plant.',
            'status': 'backlog',
            'priority': 3,
        },
        {
            'title': 'Review Flotation equipment',
            'description': 'Check cell setup, reagent handling, concentrate collection equipment for Cu oxide and V recovery.',
            'status': 'backlog',
            'priority': 2,
        },
        {
            'title': 'Review Assay equipment',
            'description': 'Validate analytical equipment for Cu, V, and critical minerals analysis. Check QA/QC procedures.',
            'status': 'backlog',
            'priority': 2,
        },
        {
            'title': 'Review Pilot Plant Auxiliary systems',
            'description': 'Evaluate utilities, support systems, and infrastructure requirements.',
            'status': 'backlog',
            'priority': 2,
        },
        {
            'title': 'Add LIMS requirement to design',
            'description': 'Document need for Laboratory Information Management System — likely missing from original design.',
            'status': 'todo',
            'priority': 4,
        },
        {
            'title': 'Add Sample Stations throughout lab',
            'description': 'Specify drop-off/pickup points for chain of custody and workflow efficiency.',
            'status': 'todo',
            'priority': 4,
        },
        {
            'title': 'Prepare equipment review tracker',
            'description': 'Populate equipment-review-tracker.md with all items from initial design.',
            'status': 'in_progress',
            'priority': 3,
        },
        {
            'title': 'Document design decisions',
            'description': 'Keep decisions-log.md updated with all changes and rationale.',
            'status': 'backlog',
            'priority': 2,
        },
        {
            'title': 'Final review and report',
            'description': 'Compile all reviews into final deliverable for client.',
            'status': 'backlog',
            'priority': 4,
            'due_date': timezone.now().date().replace(month=3, day=28),
        },
        {
            'title': 'Complete annual fire safety training',
            'description': 'Mandatory annual fire safety training for UQ staff. Complete online modules and certification.',
            'status': 'todo',
            'priority': 3,
        },
    ]
    
    for task_data in tasks:
        Task.objects.create(project=mavin, **task_data)
    
    print(f"Created {len(tasks)} tasks")
else:
    print(f"Project already exists: {mavin.name}")

print("\nSample data loaded!")
