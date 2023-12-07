from django import template
from django.conf import settings

from main.views import MainManager

register = template.Library()


# settings value
@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")


@register.filter
def is_authenticated(request):
    return request.user.is_authenticated

@register.filter
def is_lta_user(request):
    return MainManager.is_lta_user(request)
