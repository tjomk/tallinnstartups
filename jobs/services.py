from typing import List, Dict, Any
from .repositories import JobRepository, CompanyRepository
from .models import Job


class HomePageService:
    """Service for home page business logic."""
    
    def __init__(self):
        self.job_repository = JobRepository()
        self.company_repository = CompanyRepository()
    
    def get_home_page_data(self, search_query: str = None) -> Dict[str, Any]:
        """Get all data needed for the home page, optionally filtered by search query."""
        if search_query:
            return self._get_search_results(search_query)
        else:
            return {
                'categories': self._get_formatted_categories(),
                'featured_jobs': self._get_formatted_featured_jobs(),
                'latest_jobs': self._get_formatted_latest_jobs(),
                'is_search_results': False,
                'search_query': None,
                'total_results': None
            }
    
    def _get_search_results(self, query: str) -> Dict[str, Any]:
        """Get search results for the given query."""
        featured_jobs = JobRepository.search_featured_jobs(query)
        latest_jobs = JobRepository.search_latest_jobs(query)
        
        # Format the jobs
        formatted_featured = [self._format_job_data(job) for job in featured_jobs]
        formatted_latest = [self._format_job_data(job) for job in latest_jobs]
        
        # Calculate total results
        total_results = len(formatted_featured) + len(formatted_latest)
        
        return {
            'categories': self._get_formatted_categories(),
            'featured_jobs': formatted_featured,
            'latest_jobs': formatted_latest,
            'is_search_results': True,
            'search_query': query,
            'total_results': total_results
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
                'url': None
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
        }


class JobService:
    """Service for job-related business logic."""
    
    def __init__(self):
        self.job_repository = JobRepository()
    
    def get_job_details(self, job_id: int) -> Dict[str, Any]:
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