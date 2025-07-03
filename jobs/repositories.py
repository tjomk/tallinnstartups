from typing import List, Dict, Any, Optional
from django.db.models import Count, QuerySet
from django.db import models
from .models import Job, Company


class JobRepository:
    """Repository for job-related database operations."""
    
    @staticmethod
    def get_category_counts() -> QuerySet:
        """Get job counts grouped by category for visible jobs only."""
        return Job.objects.filter(
            status='live'
        ).values('category').annotate(count=Count('id')).order_by('-count')
    
    @staticmethod
    def get_featured_jobs(limit: int = 2) -> QuerySet:
        """Get featured jobs with company information."""
        return Job.objects.filter(
            status='live',
            is_featured=True
        ).select_related('company')[:limit]
    
    @staticmethod
    def get_latest_jobs(limit: int = 5) -> QuerySet:
        """Get latest jobs ordered by creation date."""
        return Job.objects.filter(
            status='live'
        ).select_related('company').order_by('-created_at')[:limit]
    
    @staticmethod
    def get_job_by_id(job_id: int) -> Optional[Job]:
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
        
        # Create case-insensitive search using ILIKE (PostgreSQL) or LIKE (SQLite)
        search_conditions = models.Q(
            title__icontains=query
        ) | models.Q(
            description__icontains=query
        )
        
        queryset = Job.objects.filter(
            search_conditions,
            status='live'
        ).select_related('company').order_by('-created_at')
        
        if limit:
            queryset = queryset[:limit]
        
        return queryset
    
    @staticmethod
    def search_featured_jobs(query: str, limit: int = 2) -> QuerySet:
        """Search featured jobs by title and description."""
        if not query:
            return Job.objects.none()
        
        search_conditions = models.Q(
            title__icontains=query
        ) | models.Q(
            description__icontains=query
        )
        
        return Job.objects.filter(
            search_conditions,
            status='live',
            is_featured=True
        ).select_related('company').order_by('-created_at')[:limit]
    
    @staticmethod
    def search_latest_jobs(query: str, limit: int = 5) -> QuerySet:
        """Search latest jobs by title and description."""
        if not query:
            return Job.objects.none()
        
        search_conditions = models.Q(
            title__icontains=query
        ) | models.Q(
            description__icontains=query
        )
        
        return Job.objects.filter(
            search_conditions,
            status='live'
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