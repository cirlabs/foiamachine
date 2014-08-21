from django.core.urlresolvers import reverse  
from django import template

register = template.Library()


from django import template
from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter
from django.utils.text import normalize_newlines

register = template.Library()

def remove_newlines(text):
    """
    Removes all newline characters from a block of text.
    """
    # First normalize the newlines using Django's nifty utility
    normalized_text = normalize_newlines(text)
    # Then simply remove the newlines like so.
    return mark_safe(normalized_text.replace('\n', ' '))
remove_newlines.is_safe = True
remove_newlines = stringfilter(remove_newlines)
register.filter(remove_newlines)

@register.simple_tag
def api_detail(resource_name, pk):  
    """Return API URL for Tastypie Resource details.

    Usage::

        {% api_detail 'entry' entry.pk %}

    or::

        {% api_detail 'api2:entry' entry.pk %}  
    """  
    if ':' in resource_name:  
        api_name, resource_name = resource_name.split(':', 1)  
    else:  
        api_name = 'api'  
    return reverse('api_dispatch_detail', kwargs={  
            'api_name': api_name,  
            'resource_name': resource_name,  
            'pk': pk  
        }) + '?format=json'
        
@register.simple_tag
def api_list(resource_name):  
    """Return API URL for Tastypie Resource list.

    Usage::

        {% api_list 'entry' %}

    or::

        {% api_list 'api2:entry' %}  
    """  
    if ':' in resource_name:  
        api_name, resource_name = resource_name.split(':', 1)  
    else:  
        api_name = 'v1'  
    return reverse('api_dispatch_list', kwargs={  
        'api_name': api_name,  
        'resource_name': resource_name,
    #}) + '?format=json'
    })