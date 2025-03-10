from django import template
from django.utils.translation import gettext_lazy as _

register = template.Library()

CSS_RIGHT_CLASS = 'right-error-msg'

@register.filter
def translate(element):
    return _(element)
