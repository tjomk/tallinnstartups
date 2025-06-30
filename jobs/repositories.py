from typing import List, Dict, Any, Optional
from django.db.models import Count, QuerySet
from .models import Job, Company


class JobRepository:
    """Repository for job-related database operations."""
    
    @staticmethod
    def get_category_counts() -> QuerySet:
        """Get job counts grouped by category."""
        return Job.objects.values('category').annotate(count=Count('id')).order_by('-count')
    
    @staticmethod
    def get_featured_jobs(limit: int = 2) -> QuerySet:
        """Get featured jobs with company information."""
        return Job.objects.filter(
            featured_until__isnull=False
        ).select_related('company')[:limit]
    
    @staticmethod
    def get_latest_jobs(limit: int = 5) -> QuerySet:
        """Get latest jobs ordered by creation date."""
        return Job.objects.select_related('company').order_by('-created_at')[:limit]
    
    @staticmethod
    def get_job_by_id(job_id: int) -> Optional[Job]:
        """Get a single job by ID with company information."""
        try:
            return Job.objects.select_related('company').get(id=job_id)
        except Job.DoesNotExist:
            return None


class CompanyRepository:
    """Repository for company-related database operations."""
    
    @staticmethod
    def get_company_by_id(company_id: int) -> Optional[Company]:
        """Get a single company by ID."""
        try:
            return Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return None
    
    @staticmethod
    def get_companies_with_job_counts() -> QuerySet:
        """Get companies with their job counts."""
        return Company.objects.annotate(job_count=Count('jobs')).order_by('-job_count')