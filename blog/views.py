from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.db.models import Q
import random
from .models import BlogArticle, BlogCategory


def blog_article_list(request):
    """List all published blog articles with pagination"""
    articles = BlogArticle.objects.filter(status='published').select_related('category')

    # Pagination
    paginator = Paginator(articles, 10)  # Show 10 articles per page
    page = request.GET.get('page')

    try:
        articles_page = paginator.page(page)
    except PageNotAnInteger:
        articles_page = paginator.page(1)
    except EmptyPage:
        articles_page = paginator.page(paginator.num_pages)

    context = {
        'articles': articles_page,
        'page_title': 'Guides - Estonian Startup Jobs',
        'meta_description': 'Expert guides and career advice for tech professionals in Estonia',
    }

    return render(request, 'blog/article_list.html', context)


def blog_article_detail(request, slug):
    """Show detailed view of a single blog article"""
    article = get_object_or_404(BlogArticle.objects.select_related('category'),
                                slug=slug, status='published')

    # Get related articles (random articles from same category)
    related_articles = []
    if article.category:
        related_articles = BlogArticle.objects.filter(
            category=article.category,
            status='published'
        ).exclude(id=article.id).order_by('?')[:3]

    context = {
        'article': article,
        'related_articles': related_articles,
        'page_title': f'{article.title} - Estonian Startup Jobs',
        'meta_description': article.meta_description or article.excerpt,
        'meta_keywords': article.meta_keywords,
    }

    return render(request, 'blog/article_detail.html', context)


def blog_category_articles(request, category_slug):
    """List all articles in a specific category"""
    category = get_object_or_404(BlogCategory, slug=category_slug)
    articles = BlogArticle.objects.filter(
        category=category,
        status='published'
    ).select_related('category')

    # Pagination
    paginator = Paginator(articles, 10)  # Show 10 articles per page
    page = request.GET.get('page')

    try:
        articles_page = paginator.page(page)
    except PageNotAnInteger:
        articles_page = paginator.page(1)
    except EmptyPage:
        articles_page = paginator.page(paginator.num_pages)

    context = {
        'category': category,
        'articles': articles_page,
        'page_title': f'{category.name} Guides - Estonian Startup Jobs',
        'meta_description': f'Guides and articles about {category.name} in the Estonian startup ecosystem',
    }

    return render(request, 'blog/category_articles.html', context)
