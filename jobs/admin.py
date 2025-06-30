from django.contrib import admin
from .models import Company, Job


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'category', 'location', 'created_at', 'is_featured']
    list_filter = ['category', 'created_at', 'company']
    search_fields = ['title', 'description', 'category', 'company__name']
    list_select_related = ['company']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'company', 'category', 'location')
        }),
        ('Job Details', {
            'fields': ('description', 'salary_range')
        }),
        ('Featured', {
            'fields': ('featured_until',),
            'description': 'Set a date to feature this job until that time'
        }),
    )
    
    def is_featured(self, obj):
        return obj.is_featured
    is_featured.boolean = True
    is_featured.short_description = 'Featured'
