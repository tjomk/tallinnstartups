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

Current URL patterns:
- `/` - Home page (landing page)
- `/jobs/` - Job listings page
- `/job/<slug>/` - Individual job detail page
- `/categories/<category>/` - Jobs filtered by category
- `/companies/` - Company directory
- `/company/<slug>/` - Individual company jobs page (SEO-friendly)
- `/salaries/` - Salary information
- `/career-advice/` - Career resources
- `/post-job/` - Job posting form
- `/job-submitted/` - Job submission success page
- `/admin/` - Django admin interface

## Database Models

### Company Model (`jobs/models.py`)
- `name`: Company name (CharField, max_length=200)
- `logo_url`: Company logo URL (URLField, optional)
- `slug`: SEO-friendly URL slug (auto-generated from company name)

### Job Model (`jobs/models.py`)
- `id`: UUID primary key (auto-generated)
- `title`: Job title (CharField, max_length=200)
- `description`: Job description (TextField)
- `salary_range`: Salary information (CharField, max_length=100)
- `category`: Job category (CharField with predefined choices)
- `location`: Job location (CharField, max_length=200)
- `company`: Foreign key to Company model
- `application_contact`: Application email/URL (CharField, max_length=255)
- `status`: Job status ('live' or 'in_review')
- `is_featured`: Featured job flag (BooleanField, default=False)
- `expires_at`: Job expiry date (DateTimeField, optional)
- `slug`: SEO-friendly URL slug (auto-generated)
- `created_at`, `updated_at`: Timestamps (auto-managed)

Available job categories: engineering, design, marketing, sales, product, operations, finance, hr, customer_support, other

## Adding New Jobs and Companies

**IMPORTANT**: Jobs must have `payment_status='verified'` to be visible on the website. The `is_visible` property requires:
1. `status='live'`
2. Non-expired `expires_at` date
3. `payment_status='verified'`

**Note**: Both Company and Job models automatically generate SEO-friendly slugs:
- Company slugs are used for company pages: `/company/<slug>/` (e.g., `/company/bolt/`)
- Job slugs are used for job detail pages: `/job/<slug>/` (e.g., `/job/senior-engineer-at-bolt-abc123/`)

### Quick Method - Using Django Shell
```bash
poetry run python manage.py shell -c "
from jobs.models import Company, Job
from datetime import timedelta
from django.utils import timezone

# Create company
company, created = Company.objects.get_or_create(
    name='Company Name',
    defaults={'logo_url': 'https://example.com/logo.png'}
)

# Create job - ALWAYS set payment_status='verified' to make it visible
job = Job.objects.create(
    title='Job Title',
    description='Job description with requirements and benefits...',
    salary_range='Salary information',
    category='engineering',  # Choose from available categories
    location='City, Country',
    company=company,
    application_contact='https://careers.company.com/job-url',
    status='live',
    payment_status='verified',  # REQUIRED for visibility
    expires_at=timezone.now() + timedelta(days=30)
)
print(f'Created: {job.title} at {company.name} (ID: {job.id})')
print(f'Job is visible: {job.is_visible}')
"
```

### Script Method - For Complex Jobs
Create a temporary Python script:
```python
import os, sys, django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tallinnstartups.settings')
django.setup()

from jobs.models import Company, Job
from django.utils import timezone
from datetime import timedelta

# Your job creation code here
company, created = Company.objects.get_or_create(...)
job = Job.objects.create(...)
```
Then run: `poetry run python script_name.py`

## Development Notes

- The project uses Poetry for dependency management instead of pip/requirements.txt
- All Django commands should be prefixed with `poetry run`
- SQLite database file (db.sqlite3) is in the root directory
- Templates support both dynamic data from views and static fallbacks
- Original `index.html` preserved as reference, new templates are in `tallinnstartups/templates/`
- Main view logic is in `tallinnstartups/views.py` with sample data for testing
- Job slugs are auto-generated from title and company name with UUID suffix for uniqueness
- Jobs with status='live' and non-expired dates are visible to public via `is_visible` property