from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse
import uuid
import math


class BlogCategory(models.Model):
    """Category model for blog articles"""
    name = models.CharField(max_length=100, unique=True, help_text="Category name")
    slug = models.SlugField(max_length=100, unique=True, help_text="SEO-friendly URL slug")
    description = models.TextField(blank=True, help_text="Category description")
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = "Blog Categories"
        ordering = ['name']


class BlogArticle(models.Model):
    """Main blog article model"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('published', 'Published'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, help_text="Article title")
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True, help_text="SEO-friendly URL slug")
    excerpt = models.TextField(help_text="Short description for blog list")
    content = models.TextField(help_text="Main article content (Markdown format)")
    
    # SEO fields
    meta_description = models.TextField(blank=True, help_text="Meta description for SEO")
    meta_keywords = models.CharField(max_length=255, blank=True, help_text="Comma-separated keywords for SEO")
    
    # Category and status
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles', help_text="Article category")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', help_text="Article status")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True, help_text="When article was/will be published")
    scheduled_at = models.DateTimeField(null=True, blank=True, help_text="When article should be published (future date)")
    
    # Featured image
    featured_image = models.URLField(blank=True, null=True, help_text="URL to featured image")
    featured_image_alt = models.CharField(max_length=200, blank=True, help_text="Alt text for featured image")
    
    def __str__(self):
        return self.title
    
    def generate_slug(self):
        """Generate SEO-friendly slug from article title"""
        base_slug = slugify(self.title)
        # Use first 8 characters of the article's UUID for uniqueness
        uuid_suffix = str(self.id)[:8]
        return f"{base_slug}-{uuid_suffix}"[:255]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_slug()
            # Ensure uniqueness (very unlikely collision with UUID)
            while BlogArticle.objects.filter(slug=self.slug).exists():
                self.slug = self.generate_slug()
        
        # Set timestamps based on status
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        elif self.status == 'scheduled' and self.scheduled_at and self.scheduled_at <= timezone.now():
            # If scheduled time has passed, publish it
            self.status = 'published'
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """Get absolute URL for the article"""
        return reverse('blog:article_detail', kwargs={'slug': self.slug})
    
    @property
    def is_published(self):
        """Check if article is published and visible"""
        if self.status != 'published':
            return False
        if self.published_at and self.published_at > timezone.now():
            return False
        return True
    
    @property
    def is_scheduled(self):
        """Check if article is scheduled for future publishing"""
        return self.status == 'scheduled' and self.scheduled_at and self.scheduled_at > timezone.now()
    
    @property
    def reading_time(self):
        """Calculate estimated reading time in minutes"""
        words_per_minute = 200
        word_count = len(self.content.split())
        return max(1, math.ceil(word_count / words_per_minute))
    
    class Meta:
        verbose_name = "Blog Article"
        verbose_name_plural = "Blog Articles"
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['published_at']),
            models.Index(fields=['category']),
            models.Index(fields=['slug']),
        ]