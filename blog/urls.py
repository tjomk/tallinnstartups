from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.blog_article_list, name='article_list'),
    path('article/<slug:slug>/', views.blog_article_detail, name='article_detail'),
    path('category/<slug:category_slug>/', views.blog_category_articles, name='category_articles'),
]