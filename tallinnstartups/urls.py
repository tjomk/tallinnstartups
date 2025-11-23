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
from django.urls import path
from django.conf import settings
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views
from jobs.api import CompaniesWithoutJobsView

urlpatterns = [
    path('_/admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('jobs/', views.jobs_list, name='jobs'),
    path('job/<slug:slug>/', views.job_detail, name='job_detail'),
    path('categories/<str:category>/', views.category_jobs, name='category_jobs'),
    path('companies/', views.companies_list, name='companies'),
    path('company/<slug:slug>/', views.company_jobs, name='company_jobs'),
    path('salaries/', views.home, name='salaries'),
    path('career-advice/', views.home, name='career_advice'),
    path('post-job/', views.post_job, name='post_job'),
    path('job-submitted/', views.job_submission_success, name='job_submission_success'),
    path('status/<uuid:job_id>/', views.job_status, name='job_status'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap'),
    path('robots.txt', lambda r: HttpResponse(
        open(settings.BASE_DIR / 'tallinnstartups' / 'static' / 'robots.txt', 'r').read(),
        content_type='text/plain'
    )),
    # API endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/companies/no-jobs/', CompaniesWithoutJobsView.as_view(), name='companies_without_jobs'),
]
