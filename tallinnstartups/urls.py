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
from django.contrib.staticfiles import views as static_views
from django.urls import re_path

from . import views

urlpatterns = [
    path('_/admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('jobs/', views.jobs_list, name='jobs'),
    path('job/<slug:slug>/', views.job_detail, name='job_detail'),
    path('categories/<str:category>/', views.category_jobs, name='category_jobs'),
    path('companies/', views.companies_list, name='companies'),
    path('salaries/', views.home, name='salaries'),
    path('career-advice/', views.home, name='career_advice'),
    path('post-job/', views.post_job, name='post_job'),
    path('job-submitted/', views.job_submission_success, name='job_submission_success'),
    re_path(r"^static/(?P<path>.*)$", static_views.serve),
]
