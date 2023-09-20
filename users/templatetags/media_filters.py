from django import template
from django.conf import settings

register = template.Library()


@register.filter()
def mediapath(value):
    if value:
        return f'{settings.MEDIA_URL}{value}'
    else:
        return '#'