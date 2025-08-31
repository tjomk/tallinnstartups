from django import forms
from django.core.validators import URLValidator, EmailValidator
from django.core.exceptions import ValidationError
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Invisible
import bleach
from urllib.parse import urlparse
from .models import Job
import re


class JobSearchForm(forms.Form):
    q = forms.CharField(
        max_length=255,
        required=False,
        strip=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search jobs...',
            'class': 'form-input'
        })
    )
    
    def clean_q(self):
        query = self.cleaned_data.get('q')
        if query:
            # Basic sanitization to prevent injection attacks
            query = re.sub(r'[<>"\';]', '', query)
            # Remove excessive whitespace
            query = re.sub(r'\s+', ' ', query).strip()
        return query


class JobSubmissionForm(forms.Form):
    COMPANY_TYPE_CHOICES = [
        ('tallinn_startup', 'Tallinn-based startup'),
        ('estonia_startup', 'Estonia-based startup'),
        ('incubator_accelerator_vc', 'Startup Incubator, Accelerator, or VC'),
    ]
    
    POST_OPTION_CHOICES = [
        ('featured', 'Featured job post: 75€/90 days'),
        ('standard', 'Standard job post: 35€/90 days'),
    ]
    
    # Step 1: Company Type
    company_type = forms.ChoiceField(
        choices=COMPANY_TYPE_CHOICES,
        required=True,
        error_messages={'required': 'Please select a company type.'}
    )
    
    # Step 2: Post Option
    post_option = forms.ChoiceField(
        choices=POST_OPTION_CHOICES,
        required=True,
        error_messages={'required': 'Please select a post option.'}
    )
    
    # Step 3: Job Description
    job_title = forms.CharField(
        max_length=200,
        required=True,
        strip=True,
        error_messages={'required': 'Job title is required.', 'max_length': 'Job title must be 200 characters or less.'}
    )
    
    company_name = forms.CharField(
        max_length=200,
        required=True,
        strip=True,
        error_messages={'required': 'Company name is required.', 'max_length': 'Company name must be 200 characters or less.'}
    )
    
    job_category = forms.ChoiceField(
        choices=Job.CATEGORY_CHOICES,
        required=True,
        error_messages={'required': 'Please select a job category.'}
    )
    
    company_website = forms.URLField(
        required=True,
        validators=[URLValidator()],
        error_messages={'required': 'Company website is required.', 'invalid': 'Please enter a valid URL.'}
    )
    
    job_description = forms.CharField(
        widget=forms.Textarea,
        required=True,
        strip=True,
        min_length=50,
        max_length=5000,
        error_messages={
            'required': 'Job description is required.',
            'min_length': 'Job description must be at least 50 characters.',
            'max_length': 'Job description must be 5000 characters or less.'
        }
    )
    
    application_contact = forms.CharField(
        max_length=255,
        required=True,
        strip=True,
        error_messages={'required': 'Application contact is required.', 'max_length': 'Application contact must be 255 characters or less.'}
    )
    
    # Step 4: Payment Details
    legal_company_name = forms.CharField(
        max_length=200,
        required=True,
        strip=True,
        error_messages={'required': 'Legal company name is required.', 'max_length': 'Legal company name must be 200 characters or less.'}
    )
    
    company_address = forms.CharField(
        widget=forms.Textarea,
        required=True,
        strip=True,
        max_length=500,
        error_messages={'required': 'Company address is required.', 'max_length': 'Company address must be 500 characters or less.'}
    )
    
    invoice_email = forms.EmailField(
        required=True,
        validators=[EmailValidator()],
        error_messages={'required': 'Invoice email is required.', 'invalid': 'Please enter a valid email address.'}
    )
    
    vat_number = forms.CharField(
        max_length=20,
        required=False,
        strip=True,
        error_messages={'max_length': 'VAT number must be 20 characters or less.'}
    )
    
    # Terms and Conditions
    terms_accepted = forms.BooleanField(
        required=True,
        error_messages={'required': 'You must accept the Terms and Conditions.'}
    )
    
    # Security Fields
    captcha = ReCaptchaField(
        widget=ReCaptchaV2Invisible,
        error_messages={'required': 'Please complete the CAPTCHA verification.'}
    )
    
    # Honeypot field (hidden, should remain empty)
    website_url = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        initial=''
    )
    
    def clean_job_title(self):
        job_title = self.cleaned_data.get('job_title')
        if job_title:
            # Remove any potential HTML/script tags
            job_title = re.sub(r'<[^>]*>', '', job_title)
            # Basic sanitization - remove potentially harmful characters
            if any(char in job_title for char in ['<', '>', '"', "'"]):
                raise ValidationError('Job title contains invalid characters.')
        return job_title
    
    def clean_company_name(self):
        company_name = self.cleaned_data.get('company_name')
        if company_name:
            # Remove any potential HTML/script tags
            company_name = re.sub(r'<[^>]*>', '', company_name)
            # Basic sanitization
            if any(char in company_name for char in ['<', '>', '"', "'"]):
                raise ValidationError('Company name contains invalid characters.')
        return company_name
    
    def clean_job_description(self):
        job_description = self.cleaned_data.get('job_description')
        if job_description:
            # Allow only safe HTML tags and attributes
            allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'ul', 'ol', 'li', 'h3', 'h4']
            allowed_attributes = {
                '*': ['class'],
                'li': ['type'],
            }
            job_description = bleach.clean(
                job_description, 
                tags=allowed_tags, 
                attributes=allowed_attributes,
                strip=True
            )
        return job_description
    
    def clean_application_contact(self):
        application_contact = self.cleaned_data.get('application_contact')
        if application_contact:
            # Check if it's an email or URL
            if '@' in application_contact:
                # Validate as email
                try:
                    EmailValidator()(application_contact)
                except ValidationError:
                    raise ValidationError('Please enter a valid email address.')
            elif application_contact.startswith(('http://', 'https://')):
                # Validate as URL
                try:
                    URLValidator()(application_contact)
                except ValidationError:
                    raise ValidationError('Please enter a valid URL.')
            else:
                raise ValidationError('Application contact must be a valid email address or URL.')
            
            # Basic sanitization
            application_contact = re.sub(r'<[^>]*>', '', application_contact)
        return application_contact
    
    def clean_vat_number(self):
        vat_number = self.cleaned_data.get('vat_number')
        if vat_number:
            # VAT number format validation (basic)
            vat_number = vat_number.upper().strip()
            # Remove spaces and dashes for validation
            clean_vat = re.sub(r'[-\s]', '', vat_number)
            # Basic format check - should be alphanumeric
            if not re.match(r'^[A-Z0-9]+$', clean_vat):
                raise ValidationError('VAT number should contain only letters and numbers.')
        return vat_number
    
    def clean_website_url(self):
        """Honeypot field validation - should be empty"""
        website_url = self.cleaned_data.get('website_url')
        if website_url:
            raise ValidationError('Automated submissions are not allowed.')
        return website_url
    
    def clean_company_website(self):
        website = self.cleaned_data.get('company_website')
        if website:
            try:
                # Basic URL validation first
                URLValidator()(website)
                
                # Parse domain and check against suspicious domains
                domain = urlparse(website).netloc.lower()
                suspicious_domains = [
                    'bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'short.link',
                    'suspicious.com', 'malware.com', 'phishing.com'
                ]
                
                if any(sus_domain in domain for sus_domain in suspicious_domains):
                    raise ValidationError('This domain is not allowed.')
                    
                # Basic checks for valid domain structure
                if not domain or '.' not in domain:
                    raise ValidationError('Please enter a valid company website.')
                    
            except ValidationError:
                raise ValidationError('Please enter a valid company website URL.')
        return website