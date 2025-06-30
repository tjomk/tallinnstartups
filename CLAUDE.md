# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Django 5.2.3 project for tracking Tallinn startups, managed with Poetry for dependency management. The project follows standard Django project structure with SQLite as the database.

## Development Setup

### Dependencies
- Python 3.12+
- Poetry (for dependency management)
- Django 5.2.3

### Installation
```bash
poetry install
```

### Database Setup
```bash
poetry run python manage.py migrate
poetry run python manage.py createsuperuser  # Optional: create admin user
```

## Common Commands

### Development Server
```bash
poetry run python manage.py runserver
```

### Database Operations
```bash
# Run migrations
poetry run python manage.py migrate

# Create new migrations
poetry run python manage.py makemigrations

# Shell access
poetry run python manage.py shell

# Collect static files
poetry run python manage.py collectstatic
```

### Django Admin
```bash
# Create superuser
poetry run python manage.py createsuperuser

# Access admin at http://localhost:8000/admin/
```

## Project Structure

```
tallinnstartups/
├── manage.py                 # Django management script
├── pyproject.toml           # Poetry configuration and dependencies
├── db.sqlite3              # SQLite database file
├── index.html              # Original static HTML (preserved)
├── jobs/                   # Django app for job functionality
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── tests.py
│   └── migrations/
└── tallinnstartups/        # Main Django project package
    ├── __init__.py
    ├── settings.py         # Django settings
    ├── urls.py            # URL routing
    ├── views.py           # Project-level views
    ├── wsgi.py            # WSGI application
    ├── asgi.py            # ASGI application
    └── templates/         # Template hierarchy
        └── tallinnstartups/
            ├── base.html           # Base template
            ├── index.html          # Landing page template
            └── components/         # Reusable template components
                ├── header.html     # Navigation header
                ├── search_bar.html # Search component
                ├── job_card.html   # Job listing card
                ├── job_categories.html # Category filters
                └── pagination.html # Pagination controls
```

## Architecture Notes

- **Framework**: Django 5.2.3 with standard project layout
- **Database**: SQLite (development) - configured in settings.py:79
- **Package Management**: Poetry with pyproject.toml configuration
- **Templates**: Django template hierarchy with component-based structure
- **Template Directory**: Configured in settings.py:58 (`tallinnstartups/templates/`)
- **Secret Key**: Uses Django's insecure development key (settings.py:23)
- **Debug Mode**: Enabled for development (settings.py:26)

## Template Structure

The project uses a modular Django template system:

- **Base Template** (`base.html`): Common HTML structure, includes Tailwind CSS, extends blocks
- **Component Templates**: Reusable UI components in `components/` directory
  - `header.html`: Navigation bar with logo, menu, search, and user profile
  - `search_bar.html`: Configurable search input with icon
  - `job_card.html`: Job listing display with company logo, title, location, salary
  - `job_categories.html`: Category filter tags with job counts
  - `pagination.html`: Page navigation with Django pagination support
- **Page Templates**: Extend base template and use components
  - `index.html`: Landing page with featured jobs, latest jobs, and search

## URL Configuration

Current URL patterns (all route to home view for testing):
- `/` - Home page (landing page)
- `/jobs/` - Job listings page
- `/companies/` - Company directory
- `/salaries/` - Salary information
- `/career-advice/` - Career resources
- `/post-job/` - Job posting form
- `/admin/` - Django admin interface

## Development Notes

- The project uses Poetry for dependency management instead of pip/requirements.txt
- All Django commands should be prefixed with `poetry run`
- SQLite database file (db.sqlite3) is in the root directory
- Templates support both dynamic data from views and static fallbacks
- Original `index.html` preserved as reference, new templates are in `tallinnstartups/templates/`
- Main view logic is in `tallinnstartups/views.py` with sample data for testing