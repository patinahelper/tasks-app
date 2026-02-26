# Use Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
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

# Run collectstatic
RUN python tasks_project/manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Start command - migrate then run server
CMD sh -c "python tasks_project/manage.py migrate && gunicorn --chdir tasks_project tasks_project.wsgi:application --bind 0.0.0.0:$PORT"
