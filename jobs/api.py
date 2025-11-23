"""
API views and serializers for the jobs app.
"""
from rest_framework import serializers, generics
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from django.utils import timezone
from .models import Company, Job


class CompanySerializer(serializers.ModelSerializer):
    """
    Serializer for Company model with additional computed fields.
    """
    live_jobs_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Company
        fields = [
            'id',
            'name',
            'slug',
            'website_url',
            'logo_url',
            'live_jobs_count',
        ]


class CompaniesWithoutJobsView(generics.ListAPIView):
    """
    API endpoint that returns companies that currently have no live jobs.

    This is useful for automation tools (like n8n) to identify which companies
    need to be checked for new job postings.

    Authentication: Requires JWT token

    Returns:
        - Companies with 0 live jobs (status='live' and not expired)
        - Includes company name, website_url, slug, and logo_url
        - Ordered by name alphabetically

    Query Parameters:
        - include_all: If set to 'true', returns ALL companies with their job counts
                      (useful for monitoring all companies, not just ones without jobs)
    """
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Annotate companies with count of live jobs
        queryset = Company.objects.annotate(
            live_jobs_count=Count(
                'jobs',
                filter=Q(
                    jobs__status='live',
                    jobs__expires_at__gt=timezone.now()
                ) | Q(
                    jobs__status='live',
                    jobs__expires_at__isnull=True
                )
            )
        )

        # Check if we should return all companies or just those without jobs
        include_all = self.request.query_params.get('include_all', 'false').lower() == 'true'

        if not include_all:
            # Only return companies with 0 live jobs
            queryset = queryset.filter(live_jobs_count=0)

        # Order by name for consistency
        return queryset.order_by('name')
