from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def hiddenTag(tagName):
    return tagName.startswith('__')

@register.filter
def excludeHiddenTags(tags):
    return [tag for tag in tags if not hiddenTag(tag.name)]

