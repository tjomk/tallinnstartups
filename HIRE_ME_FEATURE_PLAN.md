# "Hire Me" Feature Development Plan

## Overview
The "Hire Me" feature will allow individuals to post their skills and contact information for potential employers to find them. This will be a free service similar to the co-founder feature, with moderation required before posts go live. Posts will be visible for a configurable duration (default: 1 week).

## Architecture Design

### 1. Database Models

#### New Model: `HireMePost`
```python
class HireMePost(models.Model):
    STATUS_CHOICES = [
        ('in_review', 'In Review'),
        ('rejected', 'Rejected'),
        ('live', 'Live'),
        ('expired', 'Expired'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="When this post expires and is no longer visible")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_review', help_text="Current status of the post")
    title = models.CharField(max_length=200, help_text="Short title for the post (e.g., 'Senior React Developer Available')")
    description = models.TextField(help_text="Detailed description of skills, experience, and what you're looking for")
    contact_info = models.CharField(max_length=255, help_text="Email or other contact information")
    name = models.CharField(max_length=100, help_text="Your name (optional)")
    location = models.CharField(max_length=100, blank=True, help_text="Your location (optional)")
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True, help_text="SEO-friendly URL slug")

    def __str__(self):
        return f"{self.title} by {self.name or 'Anonymous'}"

    def generate_slug(self):
        """Generate SEO-friendly slug from title and UUID"""
        base_slug = slugify(self.title)
        uuid_suffix = str(self.id)[:8]
        return f"{base_slug}-{uuid_suffix}"[:255]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_slug()
            while HireMePost.objects.filter(slug=self.slug).exists():
                self.slug = self.generate_slug()
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        """Check if post has expired"""
        return self.expires_at and self.expires_at <= timezone.now()

    @property
    def is_visible(self):
        """Check if post is visible to public (live status and not expired)"""
        return self.status == 'live' and not self.is_expired

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Hire Me Post"
        verbose_name_plural = "Hire Me Posts"
```

#### New Model: `HireMeTag` (for tagging/skills)
```python
class HireMeTag(models.Model):
    name = models.CharField(max_length=50, unique=True, help_text="Tag name (e.g., 'React', 'Marketing')")
    slug = models.SlugField(max_length=50, unique=True, help_text="SEO-friendly URL slug")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']
```

#### Junction Model: `HireMePostTag`
```python
class HireMePostTag(models.Model):
    post = models.ForeignKey(HireMePost, on_delete=models.CASCADE, related_name='tags')
    tag = models.ForeignKey(HireMeTag, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'tag')
        ordering = ['-created_at']
```

### 2. Forms

#### New Form: `HireMeSubmissionForm`
```python
class HireMeSubmissionForm(forms.Form):
    # Basic information
    title = forms.CharField(
        max_length=200,
        required=True,
        strip=True,
        help_text="Short title for your post (e.g., 'Senior React Developer Available')"
    )

    name = forms.CharField(
        max_length=100,
        required=False,
        strip=True,
        help_text="Your name (optional)"
    )

    description = forms.CharField(
        widget=forms.Textarea,
        required=True,
        strip=True,
        min_length=50,
        max_length=5000,
        help_text="Describe your skills, experience, and what you're looking for"
    )

    contact_info = forms.CharField(
        max_length=255,
        required=True,
        strip=True,
        help_text="Email or other contact information"
    )

    location = forms.CharField(
        max_length=100,
        required=False,
        strip=True,
        help_text="Your location (optional)"
    )

    tags = forms.CharField(
        max_length=255,
        required=False,
        strip=True,
        help_text="Comma-separated list of skills/tags (e.g., 'React, JavaScript, Marketing')"
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
```

### 3. Services Layer

#### New Service: `HireMeService`
```python
class HireMeService:
    """Service for Hire Me post business logic."""

    def __init__(self):
        self.hire_me_repository = HireMeRepository()

    def get_hire_me_posts(self, page: int = 1, posts_per_page: int = 10, tag_slug: str = None) -> Dict[str, Any]:
        """Get paginated Hire Me posts, optionally filtered by tag."""
        if tag_slug:
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
            'tags': self._get_popular_tags()
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
            'tags': [tag.name for tag in post.tags.all()],
            'tag_slugs': [tag.slug for tag in post.tags.all()]
        }

    def _get_popular_tags(self) -> List[Dict[str, Any]]:
        """Get popular tags with counts."""
        tag_counts = self.hire_me_repository.get_tag_counts()
        return [
            {
                'name': tag['name'],
                'count': tag['count'],
                'slug': tag['slug'],
                'url': reverse('hire_me_tag', kwargs={'tag_slug': tag['slug']})
            }
            for tag in tag_counts
        ]
```

### 4. Repository Layer

#### New Repository: `HireMeRepository`
```python
class HireMeRepository:
    """Repository for Hire Me post database operations."""

    @staticmethod
    def get_all_posts() -> QuerySet:
        """Get all live, non-expired posts ordered by creation date."""
        now = timezone.now()
        return HireMePost.objects.filter(
            status='live'
        ).exclude(
            expires_at__lte=now
        ).prefetch_related('tags').order_by('-created_at')

    @staticmethod
    def get_posts_by_tag(tag_slug: str) -> QuerySet:
        """Get all live, non-expired posts with a specific tag."""
        now = timezone.now()
        return HireMePost.objects.filter(
            status='live',
            tags__tag__slug=tag_slug
        ).exclude(
            expires_at__lte=now
        ).prefetch_related('tags').order_by('-created_at').distinct()

    @staticmethod
    def get_tag_counts() -> QuerySet:
        """Get tag counts for popular tags."""
        return HireMeTag.objects.annotate(
            count=Count('posts', filter=models.Q(posts__status='live'))
        ).filter(count__gt=0).order_by('-count').values('name', 'slug', 'count')

    @staticmethod
    def get_post_by_slug(slug: str) -> Optional[HireMePost]:
        """Get a single post by slug."""
        try:
            return HireMePost.objects.prefetch_related('tags').get(slug=slug)
        except HireMePost.DoesNotExist:
            return None
```

### 5. Views

#### New Views in `tallinnstartups/views.py`
```python
def hire_me_list(request, tag_slug=None):
    """
    Hire Me posts listing page with pagination and optional tag filtering.
    """
    page = request.GET.get('page', 1)

    hire_me_service = HireMeService()
    context = hire_me_service.get_hire_me_posts(page=int(page), tag_slug=tag_slug)

    # Add breadcrumbs
    breadcrumbs = [
        {'name': 'Home', 'url': reverse('home')},
        {'name': 'Hire Me', 'url': reverse('hire_me_list')}
    ]

    if tag_slug:
        tag = get_object_or_404(HireMeTag, slug=tag_slug)
        breadcrumbs.append({
            'name': f'Tag: {tag.name}',
            'url': None
        })
        context['current_tag'] = tag

    context['hire_me_breadcrumbs'] = breadcrumbs

    return render(request, 'tallinnstartups/hire_me_list.html', context)

@ratelimit(key='ip', rate='3/h', method='POST', block=True)
def post_hire_me(request):
    """
    Hire Me posting form view with form handling.
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
        submissions_logger.info(f'Hire Me submission attempt from IP: {client_ip}, User-Agent: {user_agent}')
        form = HireMeSubmissionForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Set expiration date (7 days from now by default)
                    expires_at = timezone.now() + timedelta(days=7)

                    # Create Hire Me post
                    post = HireMePost.objects.create(
                        title=form.cleaned_data['title'],
                        description=form.cleaned_data['description'],
                        contact_info=form.cleaned_data['contact_info'],
                        name=form.cleaned_data['name'] or None,
                        location=form.cleaned_data['location'] or None,
                        expires_at=expires_at,
                        status='in_review'  # All new posts start in review
                    )

                    # Process tags
                    tags_input = form.cleaned_data['tags']
                    if tags_input:
                        self._process_tags(post, tags_input)

                    # Store submission data in session for thank you page
                    request.session['hire_me_submission'] = {
                        'post_id': str(post.id),
                        'title': post.title,
                        'name': post.name,
                        'contact_info': post.contact_info,
                        'tags': tags_input
                    }

                    # Create audit log for successful submission
                    create_audit_log(
                        ip_address=client_ip,
                        user_agent=user_agent,
                        result='success',
                        job=None,  # Not a job, but we'll reuse the log model
                        company_name=post.name or 'Anonymous',
                        job_title=post.title,
                        form_data=form.cleaned_data
                    )

                    # Log successful submission
                    submissions_logger.info(
                        f'Hire Me submission successful - ID: {post.id}, Title: {post.title}, '
                        f'IP: {client_ip}, Status: {post.status}'
                    )

                    return redirect('hire_me_submission_success')

            except Exception as e:
                # Create audit log for system error
                create_audit_log(
                    ip_address=client_ip,
                    user_agent=user_agent,
                    result='system_error',
                    error_details=str(e),
                    form_data=form.cleaned_data if form.is_valid() else None
                )

                messages.error(request, 'An error occurred while submitting your post. Please try again.')
                # Log the error
                security_logger.error(
                    f'Hire Me submission error from IP: {client_ip}, Error: {str(e)}, '
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
                f'Hire Me submission failed validation from IP: {client_ip}, '
                f'Errors: {form.errors}, User-Agent: {user_agent}'
            )
            messages.error(request, 'Please correct the errors below.')
    else:
        form = HireMeSubmissionForm()

    return render(request, 'tallinnstartups/post_hire_me.html', {'form': form})

def hire_me_submission_success(request):
    """
    Thank you page after successful Hire Me submission.
    """
    submission_data = request.session.get('hire_me_submission')
    if not submission_data:
        # If no submission data, redirect to post hire me page
        return redirect('post_hire_me')

    # Clear the session data after displaying
    if 'hire_me_submission' in request.session:
        del request.session['hire_me_submission']

    return render(request, 'tallinnstartups/hire_me_submission_success.html', {
        'submission_data': submission_data
    })

def hire_me_detail(request, slug):
    """
    Hire Me post detail page view.
    """
    post = get_object_or_404(HireMePost, slug=slug)

    # Check if post is visible (live status and not expired)
    if not post.is_visible:
        raise Http404("Post not found")

    # Build breadcrumbs
    breadcrumbs = [
        {'name': 'Home', 'url': reverse('home')},
        {'name': 'Hire Me', 'url': reverse('hire_me_list')},
        {'name': post.title, 'url': None}
    ]

    return render(request, 'tallinnstartups/hire_me_detail.html', {
        'post': post,
        'post_breadcrumbs': breadcrumbs,
    })

def _process_tags(post, tags_input):
    """Process comma-separated tags and create/associate them with the post."""
    tag_names = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
    for tag_name in tag_names:
        tag, created = HireMeTag.objects.get_or_create(
            name__iexact=tag_name,
            defaults={'name': tag_name}
        )
        if not created:
            # Update tag name to match the canonical version
            tag.name = tag_name
            tag.save()
        HireMePostTag.objects.get_or_create(post=post, tag=tag)
```

### 6. Admin Integration

#### Update `jobs/admin.py`
```python
from .models import HireMePost, HireMeTag

@admin.register(HireMePost)
class HireMePostAdmin(admin.ModelAdmin):
    list_display = ['title', 'name', 'status', 'expires_at', 'created_at', 'slug']
    list_filter = ['status', 'created_at', 'expires_at']
    search_fields = ['title', 'description', 'name', 'contact_info', 'tags__name']
    list_select_related = ['tags']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'name', 'status', 'slug')
        }),
        ('Post Details', {
            'fields': ('description', 'contact_info', 'location')
        }),
        ('Visibility', {
            'fields': ('expires_at',),
            'description': 'Control post visibility and expiration'
        }),
    )

    actions = ['mark_as_live', 'mark_as_in_review', 'mark_as_rejected']

    def mark_as_live(self, request, queryset):
        updated = queryset.update(status='live')
        self.message_user(request, f'{updated} posts marked as live.')
    mark_as_live.short_description = 'Mark selected posts as live'

    def mark_as_in_review(self, request, queryset):
        updated = queryset.update(status='in_review')
        self.message_user(request, f'{updated} posts marked as in review.')
    mark_as_in_review.short_description = 'Mark selected posts as in review'

    def mark_as_rejected(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} posts marked as rejected.')
    mark_as_rejected.short_description = 'Mark selected posts as rejected'

@admin.register(HireMeTag)
class HireMeTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'post_count']
    search_fields = ['name']
    ordering = ['name']

    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = 'Posts'
```

### 7. URL Routing

#### Update `tallinnstartups/urls.py`
```python
urlpatterns = [
    # ... existing URLs ...
    path('hire-me/', views.hire_me_list, name='hire_me_list'),
    path('hire-me/tag/<slug:tag_slug>/', views.hire_me_list, name='hire_me_tag'),
    path('hire-me/post/', views.post_hire_me, name='post_hire_me'),
    path('hire-me/submitted/', views.hire_me_submission_success, name='hire_me_submission_success'),
    path('hire-me/<slug:slug>/', views.hire_me_detail, name='hire_me_detail'),
    # ... rest of URLs ...
]
```

### 8. Templates

#### New Templates:

1. `hire_me_list.html` - Main listing page (reuses existing components)
2. `post_hire_me.html` - Submission form (similar to post_cofounder.html)
3. `hire_me_submission_success.html` - Success page
4. `hire_me_detail.html` - Detail page
5. `hire_me_card.html` - Reusable card component (similar to job_card.html)

#### Example `hire_me_card.html`:
```html
<div class="theme-job-card">
    <div class="flex flex-col justify-center flex-1">
        <p class="theme-primary-text text-base font-medium leading-normal line-clamp-1">
            {{ post.title }}
        </p>
        <p class="theme-secondary-text text-sm font-normal leading-normal line-clamp-1 mt-1">
            by {{ post.name or 'Anonymous' }}
        </p>
        {% if post.location %}
            <p class="theme-tertiary-text text-xs font-normal leading-normal line-clamp-1 mt-1">
                {{ post.location }}
            </p>
        {% endif %}
        {% if post.tags %}
            <div class="flex flex-wrap gap-1 mt-2">
                {% for tag in post.tags %}
                    <span class="theme-tag">
                        {{ tag }}
                    </span>
                {% endfor %}
            </div>
        {% endif %}
    </div>
</div>
```

### 9. Settings Configuration

#### Add to `settings.py`:
```python
# Hire Me feature settings
HIRE_ME_DEFAULT_DURATION_DAYS = 7  # Default post duration in days
```

### 10. Implementation Steps

#### Step 1: Database Setup
- Create and run migrations for new models
- Update admin interface

#### Step 2: Backend Implementation
- Create forms, services, and repositories
- Implement views and URL routing
- Add validation and security measures

#### Step 3: Frontend Implementation
- Create templates reusing existing components
- Add CSS styling (reuse existing theme classes)
- Implement responsive design

#### Step 4: Integration
- Add navigation links to header/footer
- Update sitemap.xml to include new pages
- Add SEO meta tags

#### Step 5: Testing
- Unit tests for models, forms, and services
- Integration tests for views
- Manual testing of submission flow

### 11. Reusable Components

The implementation will reuse:
- **Search bar component** - For searching Hire Me posts
- **Pagination component** - For paginated listings
- **Theme classes** - For consistent styling
- **Audit logging** - For submission tracking
- **CAPTCHA integration** - For spam prevention
- **Rate limiting** - For form submissions

### 12. Security Considerations

- **Input validation**: All form fields will be properly validated
- **Sanitization**: HTML will be stripped from descriptions
- **Rate limiting**: 3 submissions per hour per IP
- **CAPTCHA**: Invisible reCAPTCHA v2
- **Honeypot field**: To catch bots
- **Audit logging**: All submissions tracked
- **Moderation**: All posts start in review status

## Implementation Timeline

1. **Day 1**: Database models and migrations
2. **Day 2**: Forms, services, and repositories
3. **Day 3**: Views and URL routing
4. **Day 4**: Templates and frontend
5. **Day 5**: Admin integration and testing
6. **Day 6**: Final testing and deployment

## Key Benefits

- **Reuses existing architecture**: Follows the same patterns as jobs and co-founder features
- **Minimal code duplication**: Leverages existing components and services
- **Consistent user experience**: UI matches the existing site design
- **Scalable**: Can handle increased traffic with proper caching
- **Maintainable**: Clear separation of concerns and proper documentation

This plan follows the DRY principles, Clean Architecture, and Domain-Driven Design as outlined in the SKILL.md document, ensuring high code quality and maintainability.