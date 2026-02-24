# Tasks App - Django Kanban Board

A Django web application for managing tasks with a kanban board interface.

## Features

- **Kanban Board** - Drag-and-drop task management with 5 columns
- **Chat with BMO** - Send messages that I can see and respond to (great for work computer)
- **Projects** - Organize tasks by project (pre-loaded with Mavin Lab Project)
- **Task Details** - Priority levels (Low/Medium/High/Urgent), due dates, descriptions, tags
- **Dashboard** - Overview stats, urgent tasks, recent activity
- **Search & Filter** - Filter by status, project, priority
- **Responsive Design** - Works on desktop and mobile

## Project Structure

```
tasks-app/
├── README.md
├── requirements.txt
└── tasks_project/
    ├── manage.py
    ├── sample_data.py           # Pre-populates with Mavin Lab tasks
    ├── tasks_project/           # Django project settings
    │   ├── settings.py
    │   ├── urls.py
    │   ├── wsgi.py
    │   └── asgi.py
    ├── tasks/                   # Main app
    │   ├── models.py            # Project & Task models
    │   ├── views.py             # All views
    │   ├── forms.py             # Forms
    │   ├── admin.py             # Admin config
    │   └── urls.py              # URL routes
    └── templates/
        ├── base.html            # Base template with navigation
        └── tasks/               # All page templates
            ├── dashboard.html
            ├── kanban.html      # Drag-and-drop board
            ├── task_list.html
            ├── task_detail.html
            ├── task_form.html
            ├── project_list.html
            └── project_detail.html
```

## Setup (on your home computer)

### 1. Copy the files
Copy the entire `tasks-app` folder to your home computer.

### 2. Create virtual environment
```bash
cd tasks-app
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run migrations
```bash
cd tasks_project
python manage.py migrate
```

### 5. Load sample data (optional - pre-loads Mavin Lab Project)
```bash
python manage.py shell < sample_data.py
```

### 6. Create admin user (optional)
```bash
python manage.py createsuperuser
```

### 7. Run server
```bash
python manage.py runserver
```

### 8. Open browser
Go to: http://127.0.0.1:8000

## Chat with BMO

The app includes a chat interface that works on your work computer (no special network access needed):

- **How it works:** Messages are stored in the local SQLite database
- **Polling:** The page checks for new messages every 15 seconds
- **Agent poller:** A background script on Railway checks the database and responds

### To enable chat responses:

After starting Django, run the chat agent poller in a separate terminal:

```bash
cd tasks-app
python3 chat_agent_poller.py
```

This script checks for new messages every 15 seconds and generates responses.

**Note:** The poller currently provides basic responses. For full agent capabilities, continue using Telegram. The in-app chat is perfect for quick task updates at work.

## Kanban Columns

| Column | Purpose |
|--------|---------|
| **Backlog** | Ideas and future work |
| **To Do** | Ready to start |
| **In Progress** | Currently working on |
| **Review** | Needs review/testing |
| **Done** | Completed |

## Data Storage

All data is stored in `db.sqlite3` in the `tasks_project` folder. This is a single file you can backup, move, or delete to start fresh.

## Pre-loaded Content

Running `sample_data.py` creates:
- **Mavin Lab Project** with description and blue color
- **10 sample tasks** covering your main work areas:
  - Sample Prep equipment review
  - Comminution equipment review
  - Flotation equipment review
  - Assay equipment review
  - LIMS requirement (marked urgent)
  - Sample Stations (marked urgent)
  - Equipment review tracker
  - Design decisions log
  - Final report preparation

## URLs

- `/` - Dashboard
- `/kanban/` - Kanban board (main view)
- `/tasks/` - List view with filters
- `/task/new/` - Create new task
- `/projects/` - All projects
- `/admin/` - Django admin (if you created superuser)
