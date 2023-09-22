from config import settings
from django.core.cache import cache
from blog.models import Blog


def get_articles_cache():
    """Создание кеширования"""
    if settings.CACHE_ENABLED:
        key = 'articles_list'
        articles_list = cache.get(key)
        if articles_list is None:
            articles_list = Blog.objects.all()
            cache.set(key, articles_list)
        else:
            return articles_list
    else:
        articles_list = Blog.objects.all()
    return articles_list
