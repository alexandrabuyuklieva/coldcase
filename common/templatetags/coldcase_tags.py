from datetime import datetime

from django import template
from django.utils import timezone

register = template.Library()

SUSPICION_LEVELS = (
    (3, 'висок'),
    (1, 'среден'),
    (0, 'нисък'),
)


@register.simple_tag(takes_context=True)
def active_if(context, *names):
    match = getattr(context.get('request'), 'resolver_match', None)
    if match is None:
        return ''
    return 'active' if match.namespace in names or match.view_name in names else ''


@register.filter
def initials(person):
    first_name = getattr(person, 'first_name', '') or ''
    last_name = getattr(person, 'last_name', '') or ''
    return f'{first_name[:1]}{last_name[:1]}'.upper()


@register.filter
def suspicion_level(index):
    try:
        index = int(index)
    except (TypeError, ValueError):
        return SUSPICION_LEVELS[-1][1]
    return next(label for threshold, label in SUSPICION_LEVELS if index >= threshold)


@register.filter
def days_since(value):
    if not value:
        return ''
    if isinstance(value, datetime):
        value = timezone.localtime(value).date() if timezone.is_aware(value) else value.date()
    days = (timezone.localdate() - value).days
    if days <= 0:
        return 'днес'
    return f'{days} ден' if days == 1 else f'{days} дни'


@register.inclusion_tag('partials/_confidence_meter.html')
def confidence_meter(value):
    try:
        value = max(0, min(100, int(value)))
    except (TypeError, ValueError):
        value = 0
    return {'value': value, 'is_strong': value >= 70}
