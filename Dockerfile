# Use Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/tasks_project
ENV DJANGO_SETTINGS_MODULE=tasks_project.settings

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Run collectstatic from /app (not from inside tasks_project)
# PYTHONPATH ensures tasks_project is found
RUN PYTHONPATH=/app/tasks_project python tasks_project/manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Start command - run from /app, not from inside tasks_project
CMD PYTHONPATH=/app/tasks_project python tasks_project/manage.py migrate && \
    PYTHONPATH=/app/tasks_project gunicorn --chdir tasks_project tasks_project.wsgi:application --bind 0.0.0.0:$PORT
