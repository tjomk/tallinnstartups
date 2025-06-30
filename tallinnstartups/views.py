from django.shortcuts import render
from jobs.services import HomePageService


def home(request):
    """
    Home page view that displays the landing page with job listings.
    """
    home_service = HomePageService()
    context = home_service.get_home_page_data()
    
    return render(request, 'tallinnstartups/index.html', context)