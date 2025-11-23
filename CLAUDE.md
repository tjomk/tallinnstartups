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
- `/_/admin/` - Django admin interface

### API Endpoints (JWT Protected)
- `/api/token/` - Obtain JWT token (POST with username/password)
- `/api/token/refresh/` - Refresh JWT token (POST with refresh token)
- `/api/companies/no-jobs/` - Get companies without live jobs (GET with JWT auth)

## API Usage for Automation (n8n, etc.)

The project provides a secure REST API for automation tools like n8n to periodically check companies for new job postings.

### Setup: Generate JWT Token

First, create a dedicated API user via Django admin:
```bash
poetry run python manage.py createsuperuser
# Or create a regular user with manage.py shell:
poetry run python manage.py shell -c "
from django.contrib.auth.models import User
user, created = User.objects.get_or_create(
    username='n8n_automation',
    defaults={'is_staff': False, 'is_superuser': False}
)
if created:
    user.set_password('your-secure-password-here')
    user.save()
    print(f'Created API user: {user.username}')
else:
    print(f'User already exists: {user.username}')
"
```

### Get JWT Token

Request an access token:
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "n8n_automation", "password": "your-secure-password-here"}'
```

Response:
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

The access token is valid for 7 days. Store it securely in your n8n workflow.

### API Endpoint: Companies Without Jobs

**GET** `/api/companies/no-jobs/`

Returns companies that currently have no live jobs, useful for identifying which companies need job scraping.

**Authentication**: Bearer token (JWT)

**Headers**:
```
Authorization: Bearer <your-access-token>
```

**Query Parameters**:
- `include_all=true` (optional): Returns ALL companies with their job counts instead of just companies without jobs

**Example Request**:
```bash
# Get companies without jobs
curl -X GET http://localhost:8000/api/companies/no-jobs/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Get all companies with job counts
curl -X GET "http://localhost:8000/api/companies/no-jobs/?include_all=true" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Example Response**:
```json
[
  {
    "id": 1,
    "name": "Company A",
    "slug": "company-a",
    "website_url": "https://companya.com",
    "logo_url": "https://companya.com/logo.png",
    "live_jobs_count": 0
  },
  {
    "id": 5,
    "name": "Company B",
    "slug": "company-b",
    "website_url": "https://companyb.com",
    "logo_url": null,
    "live_jobs_count": 0
  }
]
```

**Use Case for n8n**:
1. Schedule a workflow to run daily/weekly
2. Call `/api/companies/no-jobs/` with JWT auth
3. For each company in the response:
   - Visit their `website_url` or careers page
   - Scrape for new job postings
   - If jobs found, notify admin or create draft job entries

**Token Refresh** (when access token expires):
```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "your-refresh-token"}'
```

Response:
```json
{
  "access": "NEW_ACCESS_TOKEN_HERE"
}
```

### Token Lifetime Configuration

Current settings (configured in `settings.py:175-181`):
- **Access Token**: Valid for 30 days
- **Refresh Token**: Valid for 90 days

For internal automation, these long-lived tokens minimize refresh overhead. Adjust in `settings.py` if needed.

### n8n Workflow Setup Options

#### Option 1: Simple Approach - Use Long-lived Access Token

With 30-day access tokens, you can simply:
1. Get initial access token
2. Store it in n8n credentials
3. Manually refresh every 30 days (or set a reminder)

**n8n HTTP Request Node Configuration**:
```
Authentication: Generic Credential Type
  - Credential Type: Header Auth
  - Name: Authorization
  - Value: Bearer YOUR_ACCESS_TOKEN_HERE
```

#### Option 2: Automatic Token Refresh (Recommended)

Build a smart n8n workflow that automatically refreshes tokens:

**Workflow Structure**:
```
1. [Schedule Trigger] - Run your job scraping workflow
2. [Check Token Expiry] - Compare stored token expiry date with current time
3. [IF Node] - Token expires in < 7 days?
   ├─ TRUE: [Refresh Token] → [Update Credentials] → [Continue]
   └─ FALSE: [Continue]
4. [Fetch Companies] - Call /api/companies/no-jobs/
5. [Process Companies] - Your scraping logic
```

**Step-by-Step Setup**:

1. **Store tokens in n8n Variables/Credentials**:
   - Go to Settings → Variables
   - Create variables:
     - `api_access_token` = your access token
     - `api_refresh_token` = your refresh token
     - `api_token_expires_at` = expiry timestamp (e.g., "2025-01-15T10:00:00Z")

2. **Add Token Refresh Logic** (before your main API call):

   **Node 1: Check if Refresh Needed** (Function node)
   ```javascript
   const expiresAt = new Date($vars.api_token_expires_at);
   const now = new Date();
   const daysUntilExpiry = (expiresAt - now) / (1000 * 60 * 60 * 24);

   return {
     needsRefresh: daysUntilExpiry < 7,
     daysUntilExpiry: Math.floor(daysUntilExpiry)
   };
   ```

   **Node 2: IF Node** - Route based on `needsRefresh`

   **Node 3: Refresh Token** (HTTP Request, only if needed)
   ```
   Method: POST
   URL: https://yourdomain.com/api/token/refresh/
   Body (JSON):
   {
     "refresh": "={{$vars.api_refresh_token}}"
   }
   ```

   **Node 4: Update Variables** (Set node)
   ```javascript
   // Update access token variable with new token
   // You'll need to use n8n's API or database to update variables
   // Or use a simpler approach with static credentials below
   ```

#### Option 3: Use n8n's Built-in Credential System

Create a **Custom Credential** in n8n:

1. Go to **Credentials** → **New** → **HTTP Header Auth**
2. Name: "Django API JWT"
3. Set header:
   - Name: `Authorization`
   - Value: `Bearer YOUR_ACCESS_TOKEN`

Then in your HTTP Request nodes:
```
Authentication: Generic Credential Type
Credential for Generic Credential Type: Django API JWT
```

When token expires (every 30 days), just update the credential once, and all workflows use the new token.

#### Option 4: Environment Variable Approach (Simplest)

If n8n runs on your server, use environment variables:
```bash
# In your n8n environment
export DJANGO_API_TOKEN="your-access-token-here"
```

In n8n HTTP Request:
```
Authorization: Bearer {{$env.DJANGO_API_TOKEN}}
```

Update the environment variable when you refresh the token.

### Complete n8n Example Workflow (JSON)

Here's a minimal working workflow you can import:

```json
{
  "nodes": [
    {
      "name": "Schedule",
      "type": "n8n-nodes-base.scheduleTrigger",
      "position": [250, 300],
      "parameters": {
        "rule": {
          "interval": [{"field": "days", "value": 1}]
        }
      }
    },
    {
      "name": "Fetch Companies Without Jobs",
      "type": "n8n-nodes-base.httpRequest",
      "position": [450, 300],
      "parameters": {
        "url": "https://yourdomain.com/api/companies/no-jobs/",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "options": {}
      },
      "credentials": {
        "httpHeaderAuth": {
          "name": "Django API JWT"
        }
      }
    },
    {
      "name": "Process Each Company",
      "type": "n8n-nodes-base.function",
      "position": [650, 300],
      "parameters": {
        "functionCode": "// Process each company\nconst companies = items[0].json;\n\nreturn companies.map(company => ({\n  json: {\n    companyName: company.name,\n    websiteUrl: company.website_url,\n    slug: company.slug\n  }\n}));"
      }
    }
  ],
  "connections": {
    "Schedule": {"main": [[{"node": "Fetch Companies Without Jobs"}]]},
    "Fetch Companies Without Jobs": {"main": [[{"node": "Process Each Company"}]]}
  }
}
```

## Database Models

### Company Model (`jobs/models.py`)
- `name`: Company name (CharField, max_length=200)
- `logo_url`: Company logo URL (URLField, optional)
- `website_url`: Company website URL (URLField, optional)
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
- `status`: Job status (CharField with choices: 'in_review', 'rejected', 'waiting_for_payment', 'refunded', 'live')
- `is_featured`: Featured job flag (BooleanField, default=False)
- `expires_at`: Job expiry date (DateTimeField, optional)
- `slug`: SEO-friendly URL slug (auto-generated)
- `created_at`, `updated_at`: Timestamps (auto-managed)

Available job categories: engineering, design, marketing, sales, product, operations, finance, hr, customer_support, other

Available job statuses: in_review, rejected, waiting_for_payment, refunded, live

## Adding New Jobs and Companies

**IMPORTANT**: Jobs must have `status='live'` to be visible on the website. The `is_visible` property requires:
1. `status='live'`
2. Non-expired `expires_at` date (or null)

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
    defaults={
        'logo_url': 'https://example.com/logo.png',
        'website_url': 'https://example.com'
    }
)

# Create job - ALWAYS set status='live' to make it visible
job = Job.objects.create(
    title='Job Title',
    description='Job description with requirements and benefits...',
    salary_range='Salary information',
    category='engineering',  # Choose from available categories
    location='City, Country',
    company=company,
    application_contact='https://careers.company.com/job-url',
    status='live',  # REQUIRED for visibility
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

### Adding Jobs from Career Pages

When adding jobs from company career pages, use WebFetch to extract job information:

```bash
# Example workflow:
# 1. Fetch career page to get job details
# 2. Fetch company website to get company description
# 3. Create company with all available fields (name, logo_url, website_url)
# 4. Create job with extracted information
```

**Complete Example:**
```bash
poetry run python manage.py shell -c "
from jobs.models import Company, Job
from datetime import timedelta
from django.utils import timezone

# Create or update company with all available information
company, created = Company.objects.get_or_create(
    name='Global Reader',
    defaults={
        'logo_url': 'https://images.squarespace-cdn.com/content/v1/64d49504ec21a0065a7ae0f2/dd68fe24-10fd-445b-9cbf-e09ae3911907/Logo%2BGR%2B3-reupload.png',
        'website_url': 'https://www.globalreader.eu'
    }
)

# If company already exists but missing website_url, update it
if not created and not company.website_url:
    company.website_url = 'https://www.globalreader.eu'
    company.save()

# Create comprehensive job description
description = '''Global Reader is an Estonian manufacturing technology company based in Tartu...

**Requirements:**
• Strong expertise in Elixir and Erlang
• Experience with Phoenix LiveView
...

**What We Offer:**
• Competitive compensation
• Flexible remote work arrangements
...'''

# Create job with all required fields
job = Job.objects.create(
    title='Elixir Developer / Senior Elixir Developer',
    description=description,
    salary_range='Competitive',  # or specific range if available
    category='engineering',
    location='Tartu, Estonia',
    company=company,
    application_contact='career@globalreader.eu',
    status='live',  # CRITICAL: Must be 'live' for visibility
    expires_at=timezone.now() + timedelta(days=60)
)

# Verify creation
print(f'✓ Created: {job.title} at {company.name}')
print(f'  Job ID: {job.id}')
print(f'  Slug: {job.slug}')
print(f'  Visible: {job.is_visible}')
print(f'  Company slug: {company.slug}')
print(f'  URLs: /job/{job.slug}/ and /company/{company.slug}/')
"
```

**Field Guidelines:**
- `name`: Use official company name with correct capitalization
- `logo_url`: Direct URL to company logo image (PNG, JPG, SVG)
- `website_url`: Company's main website URL
- `application_contact`: Email address or career page URL where candidates apply
- `salary_range`: Specific range if provided, or 'Competitive', 'Market rate', etc.
- `description`: Markdown-formatted text with company info, role details, requirements, and benefits
- `expires_at`: Typically 30-60 days from creation; use `timezone.now() + timedelta(days=60)`

## Development Notes

- The project uses Poetry for dependency management instead of pip/requirements.txt
- All Django commands should be prefixed with `poetry run`
- SQLite database file (db.sqlite3) is in the root directory
- Templates support both dynamic data from views and static fallbacks
- Original `index.html` preserved as reference, new templates are in `tallinnstartups/templates/`
- Main view logic is in `tallinnstartups/views.py` with sample data for testing
- Job slugs are auto-generated from title and company name with UUID suffix for uniqueness
- Jobs with status='live' and non-expired dates are visible to public via `is_visible` property
- Job status workflow: in_review → (rejected | waiting_for_payment) → (refunded | live)