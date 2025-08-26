from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.http import Http404
from datetime import timedelta
from jobs.services import HomePageService, CompanyService
from jobs.forms import JobSubmissionForm, JobSearchForm
from jobs.models import Job, Company


def home(request):
    """
    Home page view that displays the landing page with job listings or search results.
    """
    search_form = JobSearchForm(request.GET)
    search_query = None
    page = request.GET.get('page', 1)
    
    if search_form.is_valid() and search_form.cleaned_data.get('q'):
        search_query = search_form.cleaned_data['q']
    
    home_service = HomePageService()
    context = home_service.get_home_page_data(search_query=search_query, page=int(page))
    context['search_form'] = search_form
    
    return render(request, 'tallinnstartups/index.html', context)


def jobs_list(request):
    """
    Jobs listing page with pagination and search functionality.
    """
    search_form = JobSearchForm(request.GET)
    search_query = None
    page = request.GET.get('page', 1)
    
    if search_form.is_valid() and search_form.cleaned_data.get('q'):
        search_query = search_form.cleaned_data['q']
    
    home_service = HomePageService()
    context = home_service.get_jobs_page_data(page=int(page), search_query=search_query)
    context['search_form'] = search_form
    
    return render(request, 'tallinnstartups/jobs_list.html', context)


def post_job(request):
    """
    Job posting form view with form handling.
    """
    if request.method == 'POST':
        form = JobSubmissionForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create or get company
                    company, created = Company.objects.get_or_create(
                        name=form.cleaned_data['company_name'],
                        defaults={'logo_url': None}
                    )
                    
                    # Determine if job should be featured
                    is_featured = form.cleaned_data['post_option'] == 'featured'
                    
                    # Set expiration date (90 days from now)
                    expires_at = timezone.now() + timedelta(days=90)
                    
                    # Extract location from company address (use first line or full address)
                    company_address = form.cleaned_data['company_address']
                    location = company_address.split('\n')[0][:200]  # First line, max 200 chars
                    
                    # Create job instance
                    job = Job.objects.create(
                        title=form.cleaned_data['job_title'],
                        description=form.cleaned_data['job_description'],
                        salary_range='Competitive',  # Default value since not in form
                        category=form.cleaned_data['job_category'],
                        location=location,
                        company=company,
                        application_contact=form.cleaned_data['application_contact'],
                        is_featured=is_featured,
                        expires_at=expires_at,
                        status='in_review'  # All new jobs start in review
                    )
                    
                    # Store additional submission data in session for thank you page
                    request.session['job_submission'] = {
                        'job_id': str(job.id),
                        'job_title': job.title,
                        'company_name': company.name,
                        'post_option': form.cleaned_data['post_option'],
                        'legal_company_name': form.cleaned_data['legal_company_name'],
                        'invoice_email': form.cleaned_data['invoice_email'],
                        'company_website': form.cleaned_data['company_website'],
                        'application_contact': form.cleaned_data['application_contact'],
                        'company_address': form.cleaned_data['company_address'],
                        'vat_number': form.cleaned_data.get('vat_number', ''),
                        'company_type': form.cleaned_data['company_type']
                    }
                    
                    return redirect('job_submission_success')
                    
            except Exception as e:
                messages.error(request, 'An error occurred while submitting your job. Please try again.')
                # Log the error in production
                # logger.error(f"Job submission error: {e}")
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = JobSubmissionForm()
    
    return render(request, 'tallinnstartups/post_job.html', {'form': form})


def job_submission_success(request):
    """
    Thank you page after successful job submission.
    """
    submission_data = request.session.get('job_submission')
    if not submission_data:
        # If no submission data, redirect to post job page
        return redirect('post_job')
    
    # Clear the session data after displaying
    if 'job_submission' in request.session:
        del request.session['job_submission']
    
    return render(request, 'tallinnstartups/job_submission_success.html', {
        'submission_data': submission_data
    })


def job_detail(request, slug):
    """
    Job detail page view that displays a specific job by its slug.
    """
    job = get_object_or_404(Job, slug=slug)
    
    # Check if job is visible to public
    if not job.is_visible:
        # For non-visible jobs, show 404 instead of revealing they exist
        raise Http404("Job not found")
    
    return render(request, 'tallinnstartups/job_detail.html', {
        'job': job
    })


def category_jobs(request, category):
    """
    Category page view that displays jobs for a specific category.
    """
    # Validate category exists in choices
    valid_categories = dict(Job.CATEGORY_CHOICES)
    if category not in valid_categories:
        raise Http404("Category not found")
    
    page = request.GET.get('page', 1)
    
    home_service = HomePageService()
    context = home_service.get_category_page_data(category=category, page=int(page))
    
    return render(request, 'tallinnstartups/category_jobs.html', context)


def companies_list(request):
    """
    Companies page view that displays actively hiring companies with pagination.
    """
    page = request.GET.get('page', 1)
    
    company_service = CompanyService()
    context = company_service.get_actively_hiring_companies_page_data(page=int(page))
    
    return render(request, 'tallinnstartups/companies_list.html', context)


def company_jobs(request, slug):
    """
    Company jobs page view that displays all jobs for a specific company.
    """
    company = get_object_or_404(Company, slug=slug)
    page = request.GET.get('page', 1)
    
    # Get all visible jobs for this company
    jobs = Job.objects.filter(
        company=company,
        status='live'
    ).exclude(
        expires_at__lte=timezone.now()
    ).order_by('-is_featured', '-created_at')
    
    # Pagination (same as other pages, 10 jobs per page)
    from django.core.paginator import Paginator
    paginator = Paginator(jobs, 10)
    page_obj = paginator.get_page(page)
    
    context = {
        'company': company,
        'jobs': page_obj.object_list,
        'page_obj': page_obj,
        'total_results': paginator.count,
    }
    
    return render(request, 'tallinnstartups/company_jobs.html', context)