"""
Management command for submitting URLs to IndexNow.

Usage:
    # Submit all URLs (jobs, companies, categories, blog, static pages)
    python manage.py indexnow --all

    # Submit only job-related URLs
    python manage.py indexnow --jobs

    # Submit only company URLs
    python manage.py indexnow --companies

    # Submit only category URLs
    python manage.py indexnow --categories

    # Submit only blog URLs
    python manage.py indexnow --blog

    # Submit only static pages
    python manage.py indexnow --static

    # Submit specific URLs
    python manage.py indexnow --urls https://example.com/page1 https://example.com/page2

    # Dry run (show URLs without submitting)
    python manage.py indexnow --all --dry-run
"""
from django.core.management.base import BaseCommand
from jobs.services import IndexNowService


class Command(BaseCommand):
    help = 'Submit URLs to IndexNow for faster search engine indexing'

    def add_arguments(self, parser):
        # URL type selection
        parser.add_argument(
            '--all',
            action='store_true',
            help='Submit all URLs (jobs, companies, categories, blog, static)',
        )
        parser.add_argument(
            '--jobs',
            action='store_true',
            help='Submit all job URLs',
        )
        parser.add_argument(
            '--companies',
            action='store_true',
            help='Submit all company URLs',
        )
        parser.add_argument(
            '--categories',
            action='store_true',
            help='Submit all category URLs',
        )
        parser.add_argument(
            '--blog',
            action='store_true',
            help='Submit all blog URLs',
        )
        parser.add_argument(
            '--static',
            action='store_true',
            help='Submit static page URLs (home, jobs list, companies list)',
        )
        parser.add_argument(
            '--urls',
            nargs='+',
            help='Submit specific URLs',
        )

        # Options
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show URLs that would be submitted without actually submitting',
        )

    def handle(self, *args, **options):
        service = IndexNowService()
        urls = []

        # Collect URLs based on options
        if options['all']:
            urls = service.get_all_urls()
            self.stdout.write(f"Collecting all URLs...")
        else:
            if options['jobs']:
                job_urls = service.get_all_job_urls()
                urls.extend(job_urls)
                self.stdout.write(f"  - Jobs: {len(job_urls)} URLs")

            if options['companies']:
                company_urls = service.get_all_company_urls()
                urls.extend(company_urls)
                self.stdout.write(f"  - Companies: {len(company_urls)} URLs")

            if options['categories']:
                category_urls = service.get_all_category_urls()
                urls.extend(category_urls)
                self.stdout.write(f"  - Categories: {len(category_urls)} URLs")

            if options['blog']:
                blog_urls = service.get_all_blog_urls()
                urls.extend(blog_urls)
                self.stdout.write(f"  - Blog: {len(blog_urls)} URLs")

            if options['static']:
                static_urls = service.get_static_urls()
                urls.extend(static_urls)
                self.stdout.write(f"  - Static: {len(static_urls)} URLs")

            if options['urls']:
                urls.extend(options['urls'])
                self.stdout.write(f"  - Custom: {len(options['urls'])} URLs")

        # Remove duplicates
        urls = list(set(urls))

        if not urls:
            self.stdout.write(
                self.style.WARNING('No URLs to submit. Use --all, --jobs, --blog, --urls, etc.')
            )
            return

        self.stdout.write(f"\nTotal URLs to submit: {len(urls)}")

        # Dry run mode
        if options['dry_run']:
            self.stdout.write(self.style.WARNING('\n[DRY RUN] URLs that would be submitted:'))
            for url in sorted(urls):
                self.stdout.write(f"  {url}")
            return

        # Submit URLs
        self.stdout.write('\nSubmitting to IndexNow...')

        if len(urls) == 1:
            # Single URL submission
            result = service.submit_url(urls[0])
            if result['success']:
                self.stdout.write(
                    self.style.SUCCESS(f"Successfully submitted: {result['url']}")
                )
                self.stdout.write(f"  Status: {result['message']}")
            else:
                self.stdout.write(
                    self.style.ERROR(f"Failed to submit: {result['url']}")
                )
                self.stdout.write(f"  Error: {result['message']}")
        else:
            # Batch submission
            result = service.submit_urls(urls)
            if result['success']:
                self.stdout.write(
                    self.style.SUCCESS(f"Successfully submitted {result['url_count']} URLs")
                )
                self.stdout.write(f"  Status: {result['message']}")
            else:
                self.stdout.write(
                    self.style.ERROR(f"Failed to submit {result['url_count']} URLs")
                )
                self.stdout.write(f"  Error: {result['message']}")

        self.stdout.write('\nDone!')
