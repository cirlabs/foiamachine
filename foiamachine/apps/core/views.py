from django.views.generic.base import TemplateResponseMixin
from django.shortcuts import render_to_response
from django.template import RequestContext

from apps.supporters.models import SupportLevel

import logging
import re

logger = logging.getLogger('default')


class UrlChangeMixin(TemplateResponseMixin):
    def render_to_response(self, context):
        #if previous page was not a form page, and there's a session related_request or completed steps, flush them
        to_clear = re.search("/requests/new", self.request.path) or re.search("/requests/edit", self.request.path)
        if to_clear is None:
            logger.info('Clearing session related_request and completed_steps')
            if 'related_request' in self.request.session:
                del self.request.session['related_request']
            if 'completed_steps' in self.request.session:
                del self.request.session['completed_steps']
        return super(UrlChangeMixin, self).render_to_response(context)


def about_view(request, template_name='about.html'):
    context = {}
    return render_to_response(template_name, context, context_instance=RequestContext(request))
