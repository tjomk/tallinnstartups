from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
import random
from datetime import timedelta
from jobs.models import Company, Job


class Command(BaseCommand):
    help = 'Generate fake data for all models'

    def add_arguments(self, parser):
        parser.add_argument(
            '--companies',
            type=int,
            default=20,
            help='Number of companies to create (default: 20)'
        )
        parser.add_argument(
            '--jobs',
            type=int,
            default=100,
            help='Number of jobs to create (default: 100)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before generating new data'
        )

    def handle(self, *args, **options):
        fake = Faker()
        
        # Clear existing data if requested
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            Job.objects.all().delete()
            Company.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared.'))

        # Generate companies
        self.stdout.write(f'Generating {options["companies"]} companies...')
        companies = self.generate_companies(fake, options['companies'])
        self.stdout.write(self.style.SUCCESS(f'Created {len(companies)} companies.'))

        # Generate jobs
        self.stdout.write(f'Generating {options["jobs"]} jobs...')
        jobs = self.generate_jobs(fake, companies, options['jobs'])
        self.stdout.write(self.style.SUCCESS(f'Created {len(jobs)} jobs.'))

        self.stdout.write(self.style.SUCCESS('Fake data generation completed!'))

    def generate_companies(self, fake, count):
        """Generate fake companies."""
        companies = []
        
        # Predefined tech company names for realism
        tech_suffixes = [
            'Tech', 'Labs', 'Systems', 'Solutions', 'Technologies', 'Software',
            'Digital', 'Innovation', 'Dynamics', 'Works', 'Corp', 'Inc',
            'Studio', 'Hub', 'Group', 'Ventures', 'Partners', 'Innovations'
        ]
        
        # Generate company names
        company_names = set()
        while len(company_names) < count:
            if random.choice([True, False]):
                # Generate compound tech names
                prefix = fake.company().split()[0]
                suffix = random.choice(tech_suffixes)
                name = f"{prefix}{suffix}"
            else:
                # Generate creative names
                name = fake.company()
            
            # Ensure uniqueness
            if name not in company_names:
                company_names.add(name)
        
        for name in company_names:
            company = Company.objects.create(
                name=name,
                logo_url=f"https://via.placeholder.com/100x100?text={name.replace(' ', '')[:2]}"
            )
            companies.append(company)
        
        return companies

    def generate_jobs(self, fake, companies, count):
        """Generate fake jobs."""
        jobs = []
        
        # Job title templates by category
        job_titles = {
            'engineering': [
                'Software Engineer', 'Senior Software Engineer', 'Frontend Developer',
                'Backend Developer', 'Full Stack Developer', 'DevOps Engineer',
                'Data Engineer', 'Machine Learning Engineer', 'QA Engineer',
                'Security Engineer', 'Cloud Engineer', 'Mobile Developer',
                'Python Developer', 'Node.js Developer', 'React Developer',
                'System Administrator', 'Database Administrator', 'Site Reliability Engineer'
            ],
            'design': [
                'UI/UX Designer', 'Graphic Designer', 'Product Designer',
                'Visual Designer', 'Web Designer', 'Brand Designer',
                'Interaction Designer', 'Motion Designer', 'User Researcher',
                'Design Manager', 'Creative Director', 'Art Director'
            ],
            'marketing': [
                'Marketing Manager', 'Digital Marketing Specialist', 'Content Marketing Manager',
                'Social Media Manager', 'SEO Specialist', 'Growth Hacker',
                'Brand Manager', 'Product Marketing Manager', 'Email Marketing Specialist',
                'Marketing Analyst', 'Content Creator', 'Community Manager'
            ],
            'sales': [
                'Sales Representative', 'Account Manager', 'Business Development Manager',
                'Sales Manager', 'Customer Success Manager', 'Inside Sales Representative',
                'Sales Development Representative', 'Regional Sales Manager',
                'Enterprise Sales Manager', 'Sales Operations Manager'
            ],
            'product': [
                'Product Manager', 'Senior Product Manager', 'Product Owner',
                'Product Analyst', 'Product Designer', 'Technical Product Manager',
                'Growth Product Manager', 'Product Marketing Manager',
                'VP of Product', 'Chief Product Officer'
            ],
            'operations': [
                'Operations Manager', 'Project Manager', 'Program Manager',
                'Business Analyst', 'Data Analyst', 'Operations Analyst',
                'Process Improvement Specialist', 'Supply Chain Manager',
                'Logistics Coordinator', 'Administrative Assistant'
            ],
            'finance': [
                'Financial Analyst', 'Accountant', 'Finance Manager',
                'CFO', 'Controller', 'Treasury Analyst',
                'Investment Analyst', 'Risk Manager', 'Budget Analyst',
                'Accounts Payable Specialist', 'Accounts Receivable Specialist'
            ],
            'hr': [
                'HR Manager', 'Recruiter', 'HR Generalist',
                'Talent Acquisition Specialist', 'HR Business Partner',
                'Compensation Analyst', 'Learning and Development Manager',
                'Employee Relations Specialist', 'HR Director', 'CHRO'
            ],
            'customer_support': [
                'Customer Support Representative', 'Technical Support Specialist',
                'Customer Success Manager', 'Support Manager', 'Help Desk Technician',
                'Customer Experience Manager', 'Support Team Lead',
                'Customer Service Representative', 'Technical Support Engineer'
            ],
            'other': [
                'Consultant', 'Specialist', 'Coordinator', 'Associate',
                'Executive Assistant', 'Office Manager', 'Researcher',
                'Analyst', 'Advisor', 'Contractor'
            ]
        }
        
        # Job description templates
        description_templates = [
            "We are seeking a talented {title} to join our dynamic team. The ideal candidate will have experience in {skills} and a passion for {passion}. You will be responsible for {responsibilities}.",
            "Join our innovative team as a {title}! We're looking for someone with strong {skills} skills who can {action}. This is a great opportunity to {opportunity}.",
            "Are you a {title} looking for your next challenge? We offer {benefits} and the chance to work on {projects}. The successful candidate will {requirements}.",
            "We are hiring a {title} to help us {goal}. You should have experience with {skills} and be able to {capabilities}. We offer {perks}.",
            "Exciting opportunity for a {title} to join our growing company! We need someone who can {tasks} and has a background in {background}. Benefits include {benefits}."
        ]
        
        skills_by_category = {
            'engineering': ['Python', 'JavaScript', 'React', 'Node.js', 'Docker', 'AWS', 'Git', 'SQL', 'MongoDB', 'Kubernetes'],
            'design': ['Figma', 'Adobe Creative Suite', 'Sketch', 'Prototyping', 'User Research', 'Design Systems', 'Wireframing'],
            'marketing': ['Google Analytics', 'SEO', 'Content Creation', 'Social Media', 'Email Marketing', 'A/B Testing', 'CRM'],
            'sales': ['Salesforce', 'CRM', 'Lead Generation', 'Negotiation', 'Account Management', 'Pipeline Management'],
            'product': ['Product Management', 'Agile', 'Scrum', 'User Stories', 'Roadmapping', 'Analytics', 'A/B Testing'],
            'operations': ['Project Management', 'Process Improvement', 'Data Analysis', 'Excel', 'Automation', 'Reporting'],
            'finance': ['Excel', 'Financial Modeling', 'Accounting', 'Budget Management', 'Financial Analysis', 'ERP'],
            'hr': ['Recruitment', 'Employee Relations', 'HRIS', 'Performance Management', 'Training', 'Compliance'],
            'customer_support': ['Customer Service', 'Technical Support', 'Zendesk', 'Troubleshooting', 'Communication'],
            'other': ['Microsoft Office', 'Communication', 'Problem Solving', 'Attention to Detail', 'Teamwork']
        }
        
        salary_ranges = [
            "€30,000 - €50,000", "€40,000 - €60,000", "€50,000 - €70,000",
            "€60,000 - €80,000", "€70,000 - €90,000", "€80,000 - €100,000",
            "€90,000 - €120,000", "€100,000 - €150,000", "Competitive",
            "Negotiable", "Market Rate"
        ]
        
        locations = [
            "Tallinn, Estonia", "Tallinn", "Remote", "Hybrid - Tallinn",
            "Tartu, Estonia", "Pärnu, Estonia", "Estonia", "Remote (Europe)",
            "Tallinn Old Town", "Tallinn City Center", "Kadriorg, Tallinn"
        ]
        
        for i in range(count):
            # Random category
            category = random.choice(list(job_titles.keys()))
            
            # Random job title from category
            title = random.choice(job_titles[category])
            
            # Random company
            company = random.choice(companies)
            
            # Generate description
            template = random.choice(description_templates)
            skills = random.sample(skills_by_category[category], min(3, len(skills_by_category[category])))
            
            description = template.format(
                title=title,
                skills=', '.join(skills),
                passion=fake.bs(),
                responsibilities=fake.catch_phrase(),
                action=fake.catch_phrase(),
                opportunity=fake.catch_phrase(),
                benefits=fake.catch_phrase(),
                projects=fake.bs(),
                requirements=fake.catch_phrase(),
                goal=fake.catch_phrase(),
                capabilities=fake.catch_phrase(),
                perks=fake.catch_phrase(),
                tasks=fake.catch_phrase(),
                background=random.choice(skills)
            )
            
            # Add more detailed description
            description += f"\n\nResponsibilities:\n"
            for _ in range(random.randint(3, 6)):
                description += f"• {fake.catch_phrase()}\n"
            
            description += f"\nRequirements:\n"
            for _ in range(random.randint(3, 5)):
                description += f"• {fake.catch_phrase()}\n"
            
            description += f"\nWhat we offer:\n"
            for _ in range(random.randint(2, 4)):
                description += f"• {fake.catch_phrase()}\n"
            
            # Random dates
            created_days_ago = random.randint(0, 60)
            created_at = timezone.now() - timedelta(days=created_days_ago)
            expires_at = created_at + timedelta(days=random.randint(30, 90))
            
            job = Job.objects.create(
                title=title,
                description=description,
                salary_range=random.choice(salary_ranges),
                category=category,
                location=random.choice(locations),
                company=company,
                application_contact=fake.email(),
                is_featured=random.choice([True, False]) if random.random() < 0.2 else False,
                status=random.choice(['live', 'in_review']) if random.random() < 0.9 else 'in_review',
                created_at=created_at,
                expires_at=expires_at
            )
            
            # Update created_at manually since auto_now_add prevents it
            Job.objects.filter(id=job.id).update(created_at=created_at)
            
            jobs.append(job)
        
        return jobs