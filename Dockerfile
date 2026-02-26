# Use Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/tasks_project:$PYTHONPATH
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

# Run migrations and collect static
RUN cd tasks_project && python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Start command
CMD cd tasks_project && gunicorn tasks_project.wsgi:application --bind 0.0.0.0:$PORT
