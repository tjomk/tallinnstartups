from typing import List, Dict, Any
from django.core.paginator import Paginator
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from .repositories import JobRepository, CompanyRepository, HireMeRepository
from .models import Job, Company
import uuid
import requests

# IndexNow configuration
INDEXNOW_KEY = "c81adff745fc4a74b04fa00ec204e71d"
INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"
SITE_HOST = "estonianstartupjobs.ee"


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
                'tags': self._get_formatted_categories(),
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
            'tags': self._get_formatted_categories(),
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
        tags = []
        
        for cat in category_counts:
            category_name = dict(Job.CATEGORY_CHOICES).get(
                cat['category'], 
                cat['category'].title()
            )
            tags.append({
                'name': category_name,
                'count': cat['count'],
                'url': reverse('category_jobs', kwargs={'category': cat['category']})
            })
        
        return tags
    
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
                'tags': self._get_formatted_categories(),
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
            'tags': self._get_formatted_categories(),
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
                'slug': company.slug,
                'active_job_count': company.active_job_count
            }
            for company in page_obj
        ]
        
        return {
            'companies': formatted_companies,
            'total_results': paginator.count,
            'page_obj': page_obj
        }


class HireMeService:
    """Service for Hire Me post business logic."""

    def __init__(self):
        self.hire_me_repository = HireMeRepository()

    def get_hire_me_posts(self, page: int = 1, posts_per_page: int = 10, tag_slug: str = None, search_query: str = None) -> Dict[str, Any]:
        """Get paginated Hire Me posts, optionally filtered by tag or search query."""
        if search_query:
            posts = self.hire_me_repository.search_posts(search_query)
        elif tag_slug:
            posts = self.hire_me_repository.get_posts_by_tag(tag_slug)
        else:
            posts = self.hire_me_repository.get_all_posts()

        paginator = Paginator(posts, posts_per_page)
        page_obj = paginator.get_page(page)

        formatted_posts = [self._format_post_data(post) for post in page_obj]

        return {
            'posts': formatted_posts,
            'total_results': paginator.count,
            'page_obj': page_obj,
            'tags': self._get_popular_tags(),
            'is_search_results': bool(search_query),
            'search_query': search_query,
        }

    def _format_post_data(self, post) -> Dict[str, Any]:
        """Format post data for template consumption."""
        return {
            'title': post.title,
            'name': post.name or 'Anonymous',
            'description': post.description,
            'contact_info': post.contact_info,
            'location': post.location,
            'slug': post.slug,
            'created_at': post.created_at,
            'tags': [post_tag.tag.name for post_tag in post.tags.all()],
            'tag_slugs': [post_tag.tag.slug for post_tag in post.tags.all()]
        }

    def _get_popular_tags(self) -> List[Dict[str, Any]]:
        """Get popular tags with counts."""
        tag_counts = self.hire_me_repository.get_tag_counts()
        return [
            {
                'name': tag['tag__name'],
                'count': tag['count'],
                'slug': tag['tag__slug'],
                'url': reverse('hire_me_tag', kwargs={'tag_slug': tag['tag__slug']})
            }
            for tag in tag_counts
        ]

    def send_contact_email(self, post, form_data) -> bool:
        """Send contact email to Hire Me post owner."""
        try:
            # Construct email subject
            subject = f"New contact message about your Hire Me post: {post.title}"

            # Construct email body
            message = f"""
You have received a new contact message about your Hire Me post: "{post.title}"

From: {form_data['sender_name']}
Email: {form_data['sender_email']}

Message:
{form_data['message']}

---
This message was sent through Estonian Startup Jobs.
Post: {post.title}
Post URL: {settings.SITE_BASE_URL}{reverse('hire_me_detail', kwargs={'slug': post.slug})}
"""

            # Prepare recipient list
            recipient_list = [post.contact_info]
            
            # Add BCC email if configured
            bcc_list = []
            if hasattr(settings, 'BCC_EMAIL') and settings.BCC_EMAIL:
                bcc_list = [settings.BCC_EMAIL]

            # Send email
            send_mail(
                subject=subject,
                message=message,
                from_email='noreply@estonianstartupjobs.ee',
                recipient_list=recipient_list,
                fail_silently=False,
            )

            return True
        except Exception as e:
            # Log the error and return False
            print(f"Error sending contact email: {e}")
            return False


class IndexNowService:
    """
    Service for submitting URLs to IndexNow for faster search engine indexing.
    https://www.indexnow.org/documentation
    """

    def __init__(self, key: str = INDEXNOW_KEY, host: str = SITE_HOST):
        self.key = key
        self.host = host
        self.endpoint = INDEXNOW_ENDPOINT

    def _build_url(self, path: str) -> str:
        """Build full URL from path."""
        return f"https://{self.host}{path}"

    def submit_url(self, url: str) -> dict:
        """Submit a single URL to IndexNow."""
        params = {
            "url": url,
            "key": self.key,
        }

        try:
            response = requests.get(self.endpoint, params=params, timeout=30)
            return {
                "success": response.status_code in (200, 202),
                "status_code": response.status_code,
                "url": url,
                "message": self._get_status_message(response.status_code),
            }
        except requests.RequestException as e:
            return {
                "success": False,
                "status_code": None,
                "url": url,
                "message": str(e),
            }

    def submit_urls(self, urls: List[str]) -> dict:
        """Submit multiple URLs to IndexNow (batch submission)."""
        if not urls:
            return {"success": False, "message": "No URLs provided"}

        if len(urls) > 10000:
            return {"success": False, "message": "Maximum 10,000 URLs per request"}

        payload = {
            "host": self.host,
            "key": self.key,
            "urlList": urls,
        }

        headers = {
            "Content-Type": "application/json; charset=utf-8",
        }

        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=headers,
                timeout=60
            )
            return {
                "success": response.status_code in (200, 202),
                "status_code": response.status_code,
                "url_count": len(urls),
                "message": self._get_status_message(response.status_code),
            }
        except requests.RequestException as e:
            return {
                "success": False,
                "status_code": None,
                "url_count": len(urls),
                "message": str(e),
            }

    def _get_status_message(self, status_code: int) -> str:
        """Get human-readable message for status code."""
        messages = {
            200: "OK - URL submitted successfully",
            202: "Accepted - URL received, pending validation",
            400: "Bad Request - Invalid format",
            403: "Forbidden - Invalid key",
            422: "Unprocessable Entity - URLs don't match host",
            429: "Too Many Requests - Rate limited",
        }
        return messages.get(status_code, f"Unknown status: {status_code}")

    def get_all_job_urls(self) -> List[str]:
        """Get all live job URLs."""
        urls = []
        jobs = Job.objects.filter(status='live')

        for job in jobs:
            if job.slug:
                urls.append(self._build_url(reverse('job_detail', kwargs={'slug': job.slug})))

        return urls

    def get_all_company_urls(self) -> List[str]:
        """Get all company URLs (companies with live jobs)."""
        urls = []
        companies = Company.objects.filter(jobs__status='live').distinct()

        for company in companies:
            if company.slug:
                urls.append(self._build_url(reverse('company_jobs', kwargs={'slug': company.slug})))

        return urls

    def get_all_category_urls(self) -> List[str]:
        """Get all category URLs."""
        urls = []
        # Get categories that have live jobs
        categories = Job.objects.filter(status='live').values_list('category', flat=True).distinct()

        for category in categories:
            urls.append(self._build_url(reverse('category_jobs', kwargs={'category': category})))

        return urls

    def get_all_blog_urls(self) -> List[str]:
        """Get all published blog article URLs."""
        from blog.models import BlogArticle, BlogCategory

        urls = []

        # Blog index
        urls.append(self._build_url(reverse('blog:article_list')))

        # Blog articles
        articles = BlogArticle.objects.filter(status='published')
        for article in articles:
            if article.slug:
                urls.append(self._build_url(reverse('blog:article_detail', kwargs={'slug': article.slug})))

        # Blog categories
        categories = BlogCategory.objects.all()
        for category in categories:
            if category.slug:
                urls.append(self._build_url(reverse('blog:category_articles', kwargs={'category_slug': category.slug})))

        return urls

    def get_static_urls(self) -> List[str]:
        """Get static page URLs."""
        return [
            self._build_url("/"),
            self._build_url(reverse('jobs')),
            self._build_url(reverse('companies')),
            self._build_url(reverse('hire_me_list')),
        ]

    def get_all_urls(self) -> List[str]:
        """Get all URLs for the site."""
        urls = []
        urls.extend(self.get_static_urls())
        urls.extend(self.get_all_job_urls())
        urls.extend(self.get_all_company_urls())
        urls.extend(self.get_all_category_urls())
        urls.extend(self.get_all_blog_urls())
        return list(set(urls))  # Remove duplicates