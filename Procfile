web: PYTHONPATH=/app/tasks_project:$PYTHONPATH gunicorn --chdir tasks_project tasks_project.wsgi:application --bind 0.0.0.0:$PORT
