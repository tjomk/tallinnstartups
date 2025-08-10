from typing import List, Dict, Any
from django.core.paginator import Paginator
from django.urls import reverse
from .repositories import JobRepository, CompanyRepository
from .models import Job
import uuid


class HomePageService:
    """Service for home page business logic."""
    
    def __init__(self):
        self.job_repository = JobRepository()
        self.company_repository = CompanyRepository()
    
    def get_home_page_data(self, search_query: str = None, page: int = 1, jobs_per_page: int = 10) -> Dict[str, Any]:
        """Get all data needed for the home page, optionally filtered by search query."""
        if search_query:
            return self._get_search_results(search_query, page, jobs_per_page)
        else:
            # Get paginated latest jobs for home page
            all_latest_jobs = self.job_repository.get_all_jobs()
            paginator = Paginator(all_latest_jobs, jobs_per_page)
            page_obj = paginator.get_page(page)
            
            # Format the paginated jobs
            formatted_latest = [self._format_job_data(job) for job in page_obj]
            
            return {
                'categories': self._get_formatted_categories(),
                'featured_jobs': self._get_formatted_featured_jobs(),
                'latest_jobs': formatted_latest,
                'is_search_results': False,
                'search_query': None,
                'total_results': paginator.count,
                'page_obj': page_obj
            }
    
    def _get_search_results(self, query: str, page: int = 1, jobs_per_page: int = 10) -> Dict[str, Any]:
        """Get search results for the given query with pagination."""
        # Get all search results (without pagination for featured)
        featured_jobs = JobRepository.search_featured_jobs(query, limit=2)
        
        # Get paginated regular search results
        all_search_jobs = JobRepository.search_jobs(query)
        paginator = Paginator(all_search_jobs, jobs_per_page)
        page_obj = paginator.get_page(page)
        
        # Format the jobs
        formatted_featured = [self._format_job_data(job) for job in featured_jobs]
        formatted_paginated = [self._format_job_data(job) for job in page_obj]
        
        # Calculate total results
        total_results = paginator.count + len(formatted_featured)
        
        return {
            'categories': self._get_formatted_categories(),
            'featured_jobs': formatted_featured,
            'latest_jobs': formatted_paginated,
            'is_search_results': True,
            'search_query': query,
            'total_results': total_results,
            'page_obj': page_obj
        }
    
    def _get_formatted_categories(self) -> List[Dict[str, Any]]:
        """Get formatted category data with counts."""
        category_counts = self.job_repository.get_category_counts()
        categories = []
        
        for cat in category_counts:
            category_name = dict(Job.CATEGORY_CHOICES).get(
                cat['category'], 
                cat['category'].title()
            )
            categories.append({
                'name': category_name,
                'count': cat['count'],
                'url': reverse('category_jobs', kwargs={'category': cat['category']})
            })
        
        return categories
    
    def _get_formatted_featured_jobs(self) -> List[Dict[str, Any]]:
        """Get formatted featured jobs data."""
        featured_jobs = self.job_repository.get_featured_jobs()
        return [self._format_job_data(job) for job in featured_jobs]
    
    def _get_formatted_latest_jobs(self) -> List[Dict[str, Any]]:
        """Get formatted latest jobs data."""
        latest_jobs = self.job_repository.get_latest_jobs()
        return [self._format_job_data(job) for job in latest_jobs]
    
    def _format_job_data(self, job) -> Dict[str, Any]:
        """Format job data for template consumption."""
        return {
            'title': job.title,
            'company_name': job.company.name,
            'company_logo': job.company.logo_url or '',
            'location': job.location,
            'salary_range': job.salary_range,
            'slug': job.slug,
            'is_featured': job.is_featured,
        }
    
    def get_jobs_page_data(self, page: int = 1, jobs_per_page: int = 10, search_query: str = None) -> Dict[str, Any]:
        """Get data for the dedicated jobs listing page with pagination."""
        if search_query:
            # Use search results with pagination
            return self._get_search_results(search_query, page, jobs_per_page)
        else:
            # Get all jobs with pagination
            all_jobs = self.job_repository.get_all_jobs()
            paginator = Paginator(all_jobs, jobs_per_page)
            page_obj = paginator.get_page(page)
            
            # Format the jobs
            formatted_jobs = [self._format_job_data(job) for job in page_obj]
            
            return {
                'categories': self._get_formatted_categories(),
                'featured_jobs': [],  # No featured section on jobs listing page
                'latest_jobs': formatted_jobs,
                'is_search_results': bool(search_query),
                'search_query': search_query,
                'total_results': paginator.count,
                'page_obj': page_obj
            }
    
    def get_category_page_data(self, category: str, page: int = 1, jobs_per_page: int = 10) -> Dict[str, Any]:
        """Get data for a specific category page with pagination."""
        # Get all jobs for this category
        category_jobs = self.job_repository.get_jobs_by_category(category)
        paginator = Paginator(category_jobs, jobs_per_page)
        page_obj = paginator.get_page(page)
        
        # Format the jobs
        formatted_jobs = [self._format_job_data(job) for job in page_obj]
        
        # Get category display name
        category_display_name = dict(Job.CATEGORY_CHOICES).get(category, category.title())
        
        return {
            'category': category,
            'category_display_name': category_display_name,
            'categories': self._get_formatted_categories(),
            'jobs': formatted_jobs,
            'total_results': paginator.count,
            'page_obj': page_obj
        }


class JobService:
    """Service for job-related business logic."""
    
    def __init__(self):
        self.job_repository = JobRepository()
    
    def get_job_details(self, job_id: uuid.UUID) -> Dict[str, Any]:
        """Get detailed job information."""
        job = self.job_repository.get_job_by_id(job_id)
        if not job:
            return {}
        
        return {
            'id': job.id,
            'title': job.title,
            'description': job.description,
            'company_name': job.company.name,
            'company_logo': job.company.logo_url or '',
            'location': job.location,
            'salary_range': job.salary_range,
            'category': job.get_category_display(),
            'category_key': job.category,
            'created_at': job.created_at,
            'is_featured': job.is_featured,
            'status': job.get_status_display(),
            'is_visible': job.is_visible
        }


class CompanyService:
    """Service for company-related business logic."""
    
    def __init__(self):
        self.company_repository = CompanyRepository()
    
    def get_companies_with_stats(self) -> List[Dict[str, Any]]:
        """Get companies with their statistics."""
        companies = self.company_repository.get_companies_with_job_counts()
        return [
            {
                'id': company.id,
                'name': company.name,
                'logo_url': company.logo_url or '',
                'job_count': company.job_count
            }
            for company in companies
        ]
    
    def get_actively_hiring_companies_page_data(self, page: int = 1, companies_per_page: int = 12) -> Dict[str, Any]:
        """Get paginated data for actively hiring companies."""
        # Get all actively hiring companies
        all_companies = self.company_repository.get_actively_hiring_companies()
        paginator = Paginator(all_companies, companies_per_page)
        page_obj = paginator.get_page(page)
        
        # Format the companies
        formatted_companies = [
            {
                'id': company.id,
                'name': company.name,
                'logo_url': company.logo_url or '',
                'active_job_count': company.active_job_count
            }
            for company in page_obj
        ]
        
        return {
            'companies': formatted_companies,
            'total_results': paginator.count,
            'page_obj': page_obj
        }