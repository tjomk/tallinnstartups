from typing import List, Dict, Any, Optional
from django.db.models import Count, QuerySet
from django.db import models
from django.utils import timezone
from .models import Job, Company
import uuid


class JobRepository:
    """Repository for job-related database operations."""
    
    @staticmethod
    def get_category_counts() -> QuerySet:
        """Get job counts grouped by category for visible jobs only."""
        now = timezone.now()
        return Job.objects.filter(
            status='live'
        ).exclude(
            expires_at__lte=now
        ).values('category').annotate(count=Count('id')).order_by('-count')
    
    @staticmethod
    def get_featured_jobs(limit: int = 2) -> QuerySet:
        """Get featured jobs with company information."""
        now = timezone.now()
        return Job.objects.filter(
            status='live',
            is_featured=True
        ).exclude(
            expires_at__lte=now
        ).select_related('company')[:limit]

    @staticmethod
    def get_latest_jobs(limit: int = 5) -> QuerySet:
        """Get latest jobs ordered by creation date."""
        now = timezone.now()
        return Job.objects.filter(
            status='live'
        ).exclude(
            expires_at__lte=now
        ).select_related('company').order_by('-created_at')[:limit]

    @staticmethod
    def get_all_jobs() -> QuerySet:
        """Get all live jobs ordered by creation date for pagination."""
        now = timezone.now()
        return Job.objects.filter(
            status='live'
        ).exclude(
            expires_at__lte=now
        ).select_related('company').order_by('-created_at')

    @staticmethod
    def get_jobs_by_category(category: str) -> QuerySet:
        """Get all live jobs in a specific category ordered by creation date."""
        now = timezone.now()
        return Job.objects.filter(
            status='live',
            category=category
        ).exclude(
            expires_at__lte=now
        ).select_related('company').order_by('-created_at')
    
    @staticmethod
    def get_job_by_id(job_id: uuid.UUID) -> Optional[Job]:
        """Get a single job by ID with company information."""
        try:
            return Job.objects.select_related('company').get(id=job_id)
        except Job.DoesNotExist:
            return None
    
    @staticmethod
    def search_jobs(query: str, limit: int = None) -> QuerySet:
        """Search jobs by title and description using ILIKE."""
        if not query:
            return Job.objects.none()

        now = timezone.now()
        # Create case-insensitive search using ILIKE (PostgreSQL) or LIKE (SQLite)
        search_conditions = models.Q(
            title__icontains=query
        ) | models.Q(
            description__icontains=query
        )

        queryset = Job.objects.filter(
            search_conditions,
            status='live'
        ).exclude(
            expires_at__lte=now
        ).select_related('company').order_by('-created_at')

        if limit:
            queryset = queryset[:limit]

        return queryset

    @staticmethod
    def search_featured_jobs(query: str, limit: int = 2) -> QuerySet:
        """Search featured jobs by title and description."""
        if not query:
            return Job.objects.none()

        now = timezone.now()
        search_conditions = models.Q(
            title__icontains=query
        ) | models.Q(
            description__icontains=query
        )

        return Job.objects.filter(
            search_conditions,
            status='live',
            is_featured=True
        ).exclude(
            expires_at__lte=now
        ).select_related('company').order_by('-created_at')[:limit]

    @staticmethod
    def search_latest_jobs(query: str, limit: int = 5) -> QuerySet:
        """Search latest jobs by title and description."""
        if not query:
            return Job.objects.none()

        now = timezone.now()
        search_conditions = models.Q(
            title__icontains=query
        ) | models.Q(
            description__icontains=query
        )

        return Job.objects.filter(
            search_conditions,
            status='live'
        ).exclude(
            expires_at__lte=now
        ).select_related('company').order_by('-created_at')[:limit]


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
        """Get companies with their live job counts."""
        return Company.objects.annotate(
            job_count=Count('jobs', filter=models.Q(jobs__status='live'))
        ).order_by('-job_count')
    
    @staticmethod
    def get_actively_hiring_companies() -> QuerySet:
        """Get companies that have active, non-expired jobs."""
        now = timezone.now()
        active_jobs_filter = models.Q(
            jobs__status='live'
        ) & (
            models.Q(jobs__expires_at__isnull=True) | models.Q(jobs__expires_at__gt=now)
        )
        
        return Company.objects.filter(
            active_jobs_filter
        ).annotate(
            active_job_count=Count('jobs', filter=active_jobs_filter)
        ).filter(active_job_count__gt=0).order_by('-active_job_count').distinct()