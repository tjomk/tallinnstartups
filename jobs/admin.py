from django.contrib import admin
from .models import Company, Job, JobSubmissionLog


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'job_type', 'category', 'location', 'status', 'is_featured', 'expires_at', 'created_at', 'slug']
    list_filter = ['status', 'job_type', 'category', 'is_featured', 'created_at', 'company']
    search_fields = ['title', 'description', 'category', 'company__name']
    list_select_related = ['company']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Information', {
            'fields': ('job_type', 'title', 'company', 'category', 'location', 'status', 'slug')
        }),
        ('Job Details', {
            'fields': ('description', 'salary_range', 'application_contact')
        }),
        ('Visibility & Features', {
            'fields': ('is_featured', 'expires_at'),
            'description': 'Control job visibility and featured status'
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('company')

    actions = ['mark_as_live', 'mark_as_in_review', 'mark_as_rejected', 'mark_as_waiting_for_payment', 'mark_as_refunded', 'make_featured', 'remove_featured']

    def mark_as_live(self, request, queryset):
        updated = queryset.update(status='live')
        self.message_user(request, f'{updated} jobs marked as live.')
    mark_as_live.short_description = 'Mark selected jobs as live'

    def mark_as_in_review(self, request, queryset):
        updated = queryset.update(status='in_review')
        self.message_user(request, f'{updated} jobs marked as in review.')
    mark_as_in_review.short_description = 'Mark selected jobs as in review'

    def mark_as_rejected(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} jobs marked as rejected.')
    mark_as_rejected.short_description = 'Mark selected jobs as rejected'

    def mark_as_waiting_for_payment(self, request, queryset):
        updated = queryset.update(status='waiting_for_payment')
        self.message_user(request, f'{updated} jobs marked as waiting for payment.')
    mark_as_waiting_for_payment.short_description = 'Mark selected jobs as waiting for payment'

    def mark_as_refunded(self, request, queryset):
        updated = queryset.update(status='refunded')
        self.message_user(request, f'{updated} jobs marked as refunded.')
    mark_as_refunded.short_description = 'Mark selected jobs as refunded'

    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} jobs marked as featured.')
    make_featured.short_description = 'Make selected jobs featured'

    def remove_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} jobs removed from featured.')
    remove_featured.short_description = 'Remove featured status from selected jobs'


@admin.register(JobSubmissionLog)
class JobSubmissionLogAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'result', 'company_name', 'job_title', 'submitted_at']
    list_filter = ['result', 'submitted_at']
    search_fields = ['ip_address', 'company_name', 'job_title', 'user_agent']
    readonly_fields = ['ip_address', 'submitted_at', 'user_agent', 'result', 'job', 'company_name',
                      'job_title', 'error_details', 'form_data_hash']
    date_hierarchy = 'submitted_at'

    def has_add_permission(self, request):
        return False  # Prevent manual creation of logs

    def has_delete_permission(self, request, obj=None):
        return False  # Prevent deletion of audit logs
