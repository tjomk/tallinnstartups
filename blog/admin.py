from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import BlogCategory, BlogArticle


class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'article_count')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    
    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = 'Articles'


class BlogArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'category', 'published_at', 'view_on_site_link')
    list_filter = ('status', 'category', 'published_at')
    search_fields = ('title', 'excerpt', 'content', 'meta_keywords')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'view_on_site_link')
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'status', 'category')
        }),
        ('Content', {
            'fields': ('excerpt', 'content')
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords')
        }),
        ('Media', {
            'fields': ('featured_image', 'featured_image_alt')
        }),
        ('Timestamps', {
            'fields': ('published_at', 'scheduled_at', 'created_at', 'updated_at')
        }),
    )
    
    def view_on_site_link(self, obj):
        if obj.is_published:
            url = reverse('blog:article_detail', kwargs={'slug': obj.slug})
            return format_html('<a href="{}" target="_blank">View on site</a>', url)
        return "-"
    view_on_site_link.short_description = 'View on site'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('category')


admin.site.register(BlogCategory, BlogCategoryAdmin)
admin.site.register(BlogArticle, BlogArticleAdmin)