from django.db import models
from django.utils import timezone


class Company(models.Model):
    name = models.CharField(max_length=200)
    logo_url = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    
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
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    featured_until = models.DateTimeField(null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    salary_range = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    location = models.CharField(max_length=200)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    
    def __str__(self):
        return f"{self.title} at {self.company.name}"
    
    @property
    def is_featured(self):
        return self.featured_until and self.featured_until > timezone.now()
    
    class Meta:
        ordering = ['-created_at']
