#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tallinnstartups.settings')
django.setup()

from jobs.models import Job, Company
from django.utils import timezone
from datetime import timedelta

def create_test_data():
    """Create test data for search functionality."""
    
    # Create test companies
    tech_co, created = Company.objects.get_or_create(
        name='TechStart Estonia',
        defaults={'logo_url': None}
    )
    print(f"TechStart Estonia: {'created' if created else 'already exists'}")
    
    design_co, created = Company.objects.get_or_create(
        name='DesignHub Tallinn',
        defaults={'logo_url': None}
    )
    print(f"DesignHub Tallinn: {'created' if created else 'already exists'}")
    
    # Create test jobs
    jobs_data = [
        {
            'title': 'Senior Python Developer',
            'description': 'We are looking for a senior Python developer to join our team. Experience with Django and PostgreSQL required. Build amazing web applications.',
            'salary_range': '4000-6000 EUR',
            'category': 'engineering',
            'location': 'Tallinn, Estonia',
            'company': tech_co,
            'status': 'live',
            'is_featured': True,
            'expires_at': timezone.now() + timedelta(days=30)
        },
        {
            'title': 'React Frontend Engineer',
            'description': 'Join our frontend team to build amazing user interfaces with React and TypeScript. Work on cutting-edge web applications.',
            'salary_range': '3500-5000 EUR',
            'category': 'engineering',
            'location': 'Tallinn, Estonia',
            'company': tech_co,
            'status': 'live',
            'is_featured': False,
            'expires_at': timezone.now() + timedelta(days=45)
        },
        {
            'title': 'UX/UI Designer',
            'description': 'Create beautiful and intuitive user experiences for our products. Experience with Figma and user research required.',
            'salary_range': '3000-4500 EUR',
            'category': 'design',
            'location': 'Tallinn, Estonia',
            'company': design_co,
            'status': 'live',
            'is_featured': True,
            'expires_at': timezone.now() + timedelta(days=60)
        },
        {
            'title': 'Marketing Manager',
            'description': 'Lead our marketing efforts and develop strategies to grow our business. Experience with digital marketing required.',
            'salary_range': '3200-4800 EUR',
            'category': 'marketing',
            'location': 'Tallinn, Estonia',
            'company': design_co,
            'status': 'live',
            'is_featured': False,
            'expires_at': timezone.now() + timedelta(days=40)
        }
    ]
    
    for job_data in jobs_data:
        job, created = Job.objects.get_or_create(
            title=job_data['title'],
            company=job_data['company'],
            defaults=job_data
        )
        print(f"{job_data['title']}: {'created' if created else 'already exists'}")
    
    print(f"\nTotal jobs in database: {Job.objects.count()}")
    print(f"Live jobs: {Job.objects.filter(status='live').count()}")
    print(f"Featured jobs: {Job.objects.filter(status='live', is_featured=True).count()}")

if __name__ == '__main__':
    create_test_data()