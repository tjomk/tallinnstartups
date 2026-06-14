"""
URL configuration for tallinnstartups project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.http import HttpResponse

from . import views
from jobs.api import CompaniesWithoutJobsView
from jobs.feeds import AllPostsFeed
from jobs.services import INDEXNOW_KEY

YANDEX_VERIFICATION_HTML = open(settings.BASE_DIR / 'yandex_804af7d126488b3d.html').read()

urlpatterns = [
    path('_/admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('jobs/', views.jobs_list, name='jobs'),
    path('job/<slug:slug>/', views.job_detail, name='job_detail'),
    path('categories/<str:category>/', views.category_jobs, name='category_jobs'),
    path('companies/', views.companies_list, name='companies'),
    path('company/<slug:slug>/', views.company_jobs, name='company_jobs'),
    path('post-job/', views.post_job, name='post_job'),
    path('find-cofounder/', views.post_cofounder, name='post_cofounder'),
    path('job-submitted/', views.job_submission_success, name='job_submission_success'),
    path('status/<uuid:job_id>/', views.job_status, name='job_status'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('feed/', AllPostsFeed(), name='feed'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap'),
    path('sitemap.txt', views.sitemap_xml, name='sitemap_txt'),
    path('robots.txt', lambda r: HttpResponse(
        open(settings.BASE_DIR / 'tallinnstartups' / 'static' / 'robots.txt', 'r').read(),
        content_type='text/plain'
    )),
    # IndexNow key verification file
    path(f'{INDEXNOW_KEY}.txt', lambda r: HttpResponse(
        INDEXNOW_KEY,
        content_type='text/plain'
    )),
    # Yandex verification
    path('yandex_804af7d126488b3d.html', lambda r: HttpResponse(YANDEX_VERIFICATION_HTML, content_type='text/html')),
    path('guides/', include('blog.urls')),
    # Hire Me feature
    path('hire-me/', views.hire_me_list, name='hire_me_list'),
    path('hire-me/tag/<slug:tag_slug>/', views.hire_me_list, name='hire_me_tag'),
    path('hire-me/post/', views.post_hire_me, name='post_hire_me'),
    path('hire-me/submitted/', views.hire_me_submission_success, name='hire_me_submission_success'),
    path('hire-me/<slug:slug>/', views.hire_me_detail, name='hire_me_detail'),
    # API endpoints
    path('api/companies/no-jobs/', CompaniesWithoutJobsView.as_view(), name='companies_without_jobs'),
]
