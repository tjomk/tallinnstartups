from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.http import Http404, HttpResponse
import requests
from django.conf import settings
from datetime import timedelta
import logging
import hashlib
import json
from django_ratelimit.decorators import ratelimit
from jobs.services import HomePageService, CompanyService
from jobs.forms import JobSubmissionForm, JobSearchForm
from jobs.models import Job, Company, JobSubmissionLog
from django.urls import reverse
from django.template.loader import render_to_string

# Initialize loggers
security_logger = logging.getLogger('security')
submissions_logger = logging.getLogger('job_submissions')


def send_admin_notification_telegram(job, form_data):
    """Send Telegram notification to admin about new job submission"""
    try:
        # Format message for Telegram (using HTML formatting)
        message = f"""
🆕 <b>New Job Submission</b>

📋 <b>Job Details:</b>
• Title: {job.title}
• Company: {job.company.name}
• Category: {job.get_category_display()}
• Location: {job.location}
• Status: {job.status}
• Payment Status: {job.payment_status}
• Payment Amount: €{job.payment_amount}
• Featured: {'Yes' if job.is_featured else 'No'}
• Expires: {job.expires_at.strftime('%Y-%m-%d %H:%M UTC')}

🏢 <b>Company Information:</b>
• Legal Name: {form_data.get('legal_company_name', 'N/A')}
• Website: {form_data.get('company_website', 'N/A')}
• Address: {form_data.get('company_address', 'N/A')}
• VAT Number: {form_data.get('vat_number', 'N/A')}
• Company Type: {form_data.get('company_type', 'N/A')}

📧 <b>Contact Information:</b>
• Invoice Email: {form_data.get('invoice_email', 'N/A')}
• Application Contact: {job.application_contact}

📝 <b>Job Description:</b>
{job.description[:500]}{'...' if len(job.description) > 500 else ''}

🆔 Job ID: <code>{job.id}</code>
🔗 Admin URL: /admin/jobs/job/{job.id}/change/
"""
        
        # Send message to Telegram
        telegram_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': settings.TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(telegram_url, data=payload, timeout=10)
        response.raise_for_status()
        
        submissions_logger.info(f'Admin notification sent to Telegram for job {job.id}')
        return True
        
    except Exception as e:
        submissions_logger.error(f'Failed to send Telegram notification for job {job.id}: {str(e)}')
        return False


def create_audit_log(ip_address, user_agent, result, job=None, company_name='', job_title='', error_details='', form_data=None):
    """Create audit log entry for job submission"""
    # Create hash of form data for duplicate detection
    form_data_hash = ''
    if form_data:
        # Only hash non-sensitive fields
        hashable_data = {
            'company_name': form_data.get('company_name', ''),
            'job_title': form_data.get('job_title', ''),
            'job_category': form_data.get('job_category', ''),
            'company_website': form_data.get('company_website', ''),
        }
        data_string = json.dumps(hashable_data, sort_keys=True)
        form_data_hash = hashlib.sha256(data_string.encode()).hexdigest()
    
    JobSubmissionLog.objects.create(
        ip_address=ip_address,
        user_agent=user_agent[:500],  # Truncate if too long
        result=result,
        job=job,
        company_name=company_name[:200],
        job_title=job_title[:200],
        error_details=error_details[:1000],
        form_data_hash=form_data_hash
    )


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


@ratelimit(key='ip', rate='3/h', method='POST', block=True)
def post_job(request):
    """
    Job posting form view with form handling.
    """
    # Get client IP for logging
    client_ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if client_ip:
        client_ip = client_ip.split(',')[0]
    else:
        client_ip = request.META.get('REMOTE_ADDR')
    
    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
    
    if request.method == 'POST':
        # Log submission attempt
        submissions_logger.info(f'Job submission attempt from IP: {client_ip}, User-Agent: {user_agent}')
        form = JobSubmissionForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create or get company
                    company, created = Company.objects.get_or_create(
                        name=form.cleaned_data['company_name'],
                        defaults={'logo_url': None}
                    )
                    
                    # Determine if job should be featured and set payment amount
                    is_featured = form.cleaned_data['post_option'] == 'featured'
                    payment_amount = 75.00 if is_featured else 35.00
                    
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
                        status='in_review',  # All new jobs start in review
                        payment_status='pending',  # Payment verification required
                        payment_amount=payment_amount
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
                    
                    # Create audit log for successful submission
                    create_audit_log(
                        ip_address=client_ip,
                        user_agent=user_agent,
                        result='success',
                        job=job,
                        company_name=company.name,
                        job_title=job.title,
                        form_data=form.cleaned_data
                    )
                    
                    # Log successful submission
                    submissions_logger.info(
                        f'Job submission successful - ID: {job.id}, Company: {company.name}, '
                        f'Title: {job.title}, IP: {client_ip}, Payment Status: {job.payment_status}'
                    )
                    
                    # Send admin notification to Telegram about new job submission
                    send_admin_notification_telegram(job, form.cleaned_data)
                    
                    return redirect('job_submission_success')
                    
            except Exception as e:
                # Create audit log for system error
                create_audit_log(
                    ip_address=client_ip,
                    user_agent=user_agent,
                    result='system_error',
                    error_details=str(e),
                    form_data=form.cleaned_data if form.is_valid() else None
                )
                
                messages.error(request, 'An error occurred while submitting your job. Please try again.')
                # Log the error
                security_logger.error(
                    f'Job submission error from IP: {client_ip}, Error: {str(e)}, '
                    f'User-Agent: {user_agent}'
                )
        else:
            # Create audit log for validation error
            create_audit_log(
                ip_address=client_ip,
                user_agent=user_agent,
                result='validation_error',
                error_details=str(form.errors),
                form_data=request.POST.dict()
            )
            
            # Log form validation errors
            security_logger.warning(
                f'Job submission failed validation from IP: {client_ip}, '
                f'Errors: {form.errors}, User-Agent: {user_agent}'
            )
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
    
    # Build breadcrumbs
    breadcrumbs = [
        {'name': 'Home', 'url': reverse('home')},
        {'name': f'{job.get_category_display()} Jobs', 'url': reverse('category_jobs', args=[job.category])},
        {'name': f'{job.title} at {job.company.name}', 'url': None}
    ]
    
    return render(request, 'tallinnstartups/job_detail.html', {
        'job': job,
        'job_breadcrumbs': breadcrumbs
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
    
    # Add breadcrumbs
    category_display_name = valid_categories[category]
    breadcrumbs = [
        {'name': 'Home', 'url': reverse('home')},
        {'name': 'All Jobs', 'url': reverse('jobs')},
        {'name': f'{category_display_name} Jobs', 'url': None}
    ]
    context['category_breadcrumbs'] = breadcrumbs
    
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
    
    # Build breadcrumbs
    breadcrumbs = [
        {'name': 'Home', 'url': reverse('home')},
        {'name': 'Companies', 'url': reverse('companies')},
        {'name': f'{company.name}', 'url': None}
    ]
    
    context = {
        'company': company,
        'jobs': page_obj.object_list,
        'page_obj': page_obj,
        'total_results': paginator.count,
        'company_breadcrumbs': breadcrumbs,
    }
    
    return render(request, 'tallinnstartups/company_jobs.html', context)


def privacy_policy(request):
    """
    Privacy policy page view.
    """
    return render(request, 'tallinnstartups/privacy_policy.html')


def terms_of_service(request):
    """
    Terms of service page view.
    """
    return render(request, 'tallinnstartups/terms_of_service.html')


def sitemap_xml(request):
    """
    Generate XML sitemap for SEO
    """
    # Get all visible jobs (live, not expired, payment verified)
    jobs = Job.objects.filter(
        status='live',
        payment_status='verified'
    ).exclude(
        expires_at__lte=timezone.now()
    ).select_related('company')
    
    # Get all companies with at least one visible job
    companies = Company.objects.filter(
        jobs__status='live',
        jobs__payment_status='verified'
    ).exclude(
        jobs__expires_at__lte=timezone.now()
    ).distinct()
    
    # Get job categories with active jobs
    job_categories = Job.objects.filter(
        status='live',
        payment_status='verified'
    ).exclude(
        expires_at__lte=timezone.now()
    ).values_list('category', flat=True).distinct()
    
    # Build sitemap data
    sitemap_data = {
        'jobs': jobs,
        'companies': companies,
        'job_categories': job_categories,
        'category_choices': dict(Job.CATEGORY_CHOICES),
        'request': request,
        'last_modified': timezone.now().strftime('%Y-%m-%d')
    }
    
    xml_content = render_to_string('tallinnstartups/sitemap.xml', sitemap_data)
    return HttpResponse(xml_content, content_type='application/xml')