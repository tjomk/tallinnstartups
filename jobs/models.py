from django.db import models
from django.utils import timezone
from django.utils.text import slugify
import uuid


class Company(models.Model):
    name = models.CharField(max_length=200)
    logo_url = models.URLField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True, help_text="Company website URL")
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True, help_text="SEO-friendly URL slug")
    
    def __str__(self):
        return self.name
    
    def generate_slug(self):
        """Generate SEO-friendly slug from company name"""
        return slugify(self.name)[:255]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = self.generate_slug()
            self.slug = base_slug
            # Ensure uniqueness by appending numbers if needed
            counter = 1
            while Company.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = "companies"


class Job(models.Model):
    CATEGORY_CHOICES = [
        ('engineering', 'Engineering'),
        ('design', 'Design'),
        ('marketing', 'Marketing'),
        ('sales', 'Sales'),
        ('product', 'Product'),
        ('operations', 'Operations'),
        ('finance', 'Finance'),
        ('hr', 'Human Resources'),
        ('customer_support', 'Customer Support'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('in_review', 'In Review'),
        ('rejected', 'Rejected'),
        ('waiting_for_payment', 'Waiting for Payment'),
        ('refunded', 'Refunded'),
        ('live', 'Live'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="When this job ad expires and is no longer visible")
    is_featured = models.BooleanField(default=False, help_text="Whether this job is featured")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_review', help_text="Current status of the job posting")
    title = models.CharField(max_length=200)
    description = models.TextField()
    salary_range = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    location = models.CharField(max_length=200)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    application_contact = models.CharField(max_length=255, default="", help_text="Email or URL for job applications")
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True, help_text="SEO-friendly URL slug")
    
    def __str__(self):
        return f"{self.title} at {self.company.name}"
    
    def generate_slug(self):
        """Generate SEO-friendly slug from job title and company name with UUID suffix"""
        base_slug = slugify(f"{self.title} at {self.company.name}")
        # Use first 8 characters of the job's UUID for uniqueness
        uuid_suffix = str(self.id)[:8]
        return f"{base_slug}-{uuid_suffix}"[:255]  # Ensure it fits in the field
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_slug()
            # Ensure uniqueness (very unlikely collision with UUID)
            while Job.objects.filter(slug=self.slug).exists():
                self.slug = self.generate_slug()
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """Check if job has expired"""
        return self.expires_at and self.expires_at <= timezone.now()

    @property
    def is_visible(self):
        """Check if job is visible to public (live status and not expired)"""
        if self.status != 'live':
            return False
        if self.is_expired:
            return False
        return True

    @property
    def is_accessible(self):
        """Check if job can be accessed via direct link (live status, regardless of expiry)"""
        return self.status == 'live'
    
    class Meta:
        ordering = ['-created_at']


class JobSubmissionLog(models.Model):
    """Audit trail for job submissions"""
    RESULT_CHOICES = [
        ('success', 'Success'),
        ('validation_error', 'Validation Error'),
        ('system_error', 'System Error'),
        ('rate_limited', 'Rate Limited'),
        ('spam_detected', 'Spam Detected'),
    ]
    
    ip_address = models.GenericIPAddressField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField(blank=True)
    result = models.CharField(max_length=20, choices=RESULT_CHOICES)
    job = models.ForeignKey(Job, null=True, blank=True, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200, blank=True)
    job_title = models.CharField(max_length=200, blank=True)
    error_details = models.TextField(blank=True)
    form_data_hash = models.CharField(max_length=64, blank=True)  # SHA256 hash for duplicate detection
    
    def __str__(self):
        return f"{self.ip_address} - {self.result} - {self.submitted_at}"
    
    class Meta:
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['ip_address', 'submitted_at']),
            models.Index(fields=['result', 'submitted_at']),
        ]
