from django.contrib import admin
from .models import Company, Job


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'category', 'location', 'status', 'is_featured', 'expires_at', 'created_at', 'slug']
    list_filter = ['status', 'category', 'is_featured', 'created_at', 'company']
    search_fields = ['title', 'description', 'category', 'company__name']
    list_select_related = ['company']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'company', 'category', 'location', 'status', 'slug')
        }),
        ('Job Details', {
            'fields': ('description', 'salary_range')
        }),
        ('Visibility & Features', {
            'fields': ('is_featured', 'expires_at'),
            'description': 'Control job visibility and featured status'
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('company')
    
    actions = ['mark_as_live', 'mark_as_in_review', 'make_featured', 'remove_featured']
    
    def mark_as_live(self, request, queryset):
        updated = queryset.update(status='live')
        self.message_user(request, f'{updated} jobs marked as live.')
    mark_as_live.short_description = 'Mark selected jobs as live'
    
    def mark_as_in_review(self, request, queryset):
        updated = queryset.update(status='in_review')
        self.message_user(request, f'{updated} jobs marked as in review.')
    mark_as_in_review.short_description = 'Mark selected jobs as in review'
    
    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} jobs marked as featured.')
    make_featured.short_description = 'Make selected jobs featured'
    
    def remove_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} jobs removed from featured.')
    remove_featured.short_description = 'Remove featured status from selected jobs'
