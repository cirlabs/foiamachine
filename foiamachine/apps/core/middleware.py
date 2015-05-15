from django.views.generic.base import TemplateResponseMixin
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect, HttpResponse
from django.utils.http import urlquote 
from django.conf import settings
from django.core import mail
from django.utils import timezone
from django.utils.cache import add_never_cache_headers
from apps.users.models import UserProfile

import json

from re import compile

import logging, pytz, re

logger = logging.getLogger('default')

EXEMPT_URLS = [compile(settings.LOGIN_URL.lstrip('/'))]
if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
    EXEMPT_URLS += [compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]

class LoginRequiredMiddleware:
    """
    Middleware that requires a user to be authenticated to view any page other
    than LOGIN_URL. Exemptions to this requirement can optionally be specified
    in settings via a list of regular expressions in LOGIN_EXEMPT_URLS (which
    you can copy from your urls.py).

    Requires authentication middleware and template context processors to be
    loaded. You'll get an error if they aren't.
    """
    def process_request(self, request):
        assert hasattr(request, 'user'), "The Login Required middleware\
            requires authentication middleware to be installed. Edit your\
            MIDDLEWARE_CLASSES setting to insert\
            'django.contrib.auth.middlware.AuthenticationMiddleware'. If that doesn't\
            work, ensure your TEMPLATE_CONTEXT_PROCESSORS setting includes\
            'django.core.context_processors.auth'."
        if not request.user.is_authenticated():
            path = request.path_info.lstrip('/')
            if not any(m.match(path) for m in EXEMPT_URLS):
                return HttpResponseRedirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

class SessionCleanser:
    def process_request(self, request):
        #if previous page was not a form page, and there's a session related_request or completed steps, flush them
        these_exemptions = ['/api/v1/contact', '/api/v1/agency', '/favicon.ico']
        if any(re.search(exempt_url, request.path) for exempt_url in these_exemptions):
            logger.info('SessionCleanser: exempt url %s' % request.path)
            return None

        to_clear = re.search("/requests/new", request.path) or re.search("/requests/edit", request.path)
        if to_clear is None:
            logger.info('Clearing session related_request and completed_steps path=%s' % request.path)
            if 'related_request' in request.session:
                del request.session['related_request']
            if  'completed_steps' in request.session:
                del request.session['completed_steps']
        return None



class DisableClientSideCachingMiddleware(object):

    def process_response(self, request, response):
        if request.path not in ['/api/v1/agency/', '/agencies/', '/requests/new/', '/requests/free-form/']:
            add_never_cache_headers(response)
        else:
            response['Cache-Control'] = 'max-age=300'
        return response

class PrependWWWSSL(object):
    '''
    sslyify overwrites the url without taking PREPEND_WWW into account.
    this simple middleware corrects for that
    '''
    def process_request(self, request):
        host = request.get_host()
        old_url = [host, request.path]
        new_url = old_url[:]
        print "PREPEND host=%s old_url=%s new_url=%s" % (host, old_url, new_url)
        '''
        if not settings.DEBUG and settings.PREPEND_WWW_SSL and old_url[0] and not old_url[0].startswith('www.'):
            new_url[0] = 'www.' + old_url[0]
            newurl = "%s://%s%s" % (
                'https' if request.is_secure() else 'http',
                new_url[0], urlquote(new_url[1]))
            return HttpResponsePermanentRedirect(new_url)
        '''

class SSLifyMiddleware(object):
    """Force all requests to use HTTPs. If we get an HTTP request, we'll just
    force a redirect to HTTPs.

    .. note::
        This will only take effect if ``settings.DEBUG`` is False.

    .. note::
        You can also disable this middleware when testing by setting
        ``settings.SSLIFY_DISABLE`` to True
    """
    def process_request(self, request):
        # disabled for test mode?
        if getattr(settings, 'SSLIFY_DISABLE', False) and \
                hasattr(mail, 'outbox'):
            return None

        # proceed as normal
        if not any((settings.DEBUG, request.is_secure())):
            url = request.build_absolute_uri(request.get_full_path())
            secure_url = url.replace('http://', 'https://')
            print "1stURL %s %s" % (url, secure_url)
            if getattr(settings, 'SSL_PREPEND_WWW', False) and ('https://www.' not in secure_url):
                secure_url = secure_url.replace("https://", "https://www.")
            print "2ndURL %s %s" % (url, secure_url)
            return HttpResponsePermanentRedirect(secure_url)

class NFOICMiddleware(object):

    def process_request(self, request):
        org_names = [
            'The Alabama Center for Open Government',
            'The Alaska FOI Coalition',
            'The First Amendment Coalition of Arizona, Inc.',
            'The Arkansas Coalition for Open Government',
            'Californians Aware',
            'The First Amendment Coalition',
            'The First Amendment Project',
            'The Colorado Freedom of Information Council',
            'The Connecticut Foundation for Open Government',
            'The New England First Amendment Coalition',
            'The Delaware Coalition for Open Government',
            'The D.C. Open Government Coalition',
            'The Brechner Center for Freedom of Information',
            'The Florida First Amendment Foundation',
            'The Marion Brechner First Amendment Project',
            'The Georgia First Amendment Foundation',
            'The Media Council Hawaii',
            'The Open Government Coalition of Hawaii',
            'The Office of Information Practices',
            'The Idahoans for Openness in Government',
            'The Citizen Advocacy Center',
            'The Illinois First Amendment Center',
            'The Indiana Coalition for Open Government',
            'The Iowa Freedom of Information Council',
            'The Kansas Sunshine Coalition for Open Government',
            'The Scripps Howard First Amendment Center',
            'The Louisiana Coalition for Open Government',
            'The Public Affairs Research Council of Louisiana',
            'The New Orleans Coalition on Open Governance',
            'The Maine Freedom of Information Coalition',
            'The New England First Amendment Coalition',
            'The Maryland Foundation for Open Government',
            'The New England First Amendment Coalition',
            'The Michigan Coalition for Open Government',
            'The Minnesota Coalition on Government Information',
            'The Missouri Sunshine Coalition',
            'The Mississippi Center for Freedom of Information',
            'The Montana Freedom of Information Hotline, Inc.',
            'The New England First Amendment Coalition',
            'The New England First Amendment Coalition',
            'The New Jersey Foundation for Open Government',
            'The New Mexico Foundation for Open Government',
            'Reinvent Albany',
            'The Tully Center for Free Speech',
            'The North Carolina Open Government Coalition',
            'The Ohio Coalition for Open Government',
            'The Ohio Media Law Center for Ethics and Access',
            'FOI Oklahoma, Inc.',
            'The Open Oregon: A Freedom of Information Coalition',
            'The Pennsylvania Freedom of Information Coalition',
            'Access/RI',
            'The New England First Amendment Coalition',
            'The South Carolina Press Association FOI Committee',
            'The Tennessee Coalition for Open Government',
            'The Freedom of Information Foundation of Texas, Inc.',
            'The Utah Foundation for Open Government',
            'The New England First Amendment Coalition',
            'The Virginia Coalition for Open Government',
            'The Freedom Foundation',
            'The Washington Coalition for Open Government',
            'The Wisconsin Freedom of Information Council',
            'The Lucy Burns Institute',
            'The West Virginia Open Government Coalition',
            'The Wyoming Coalition for Open Government'
        ]
        try:
            org_idx = request.GET.get("org")
            org_name = org_names[int(org_idx)]
            request.session['org_name'] = org_name
        except:
            pass

class TimezoneMiddleware(object):
    """ Set timezone if possible from session """

    def process_request(self, request):
        tz = request.session.get('timezone')

        if tz:
            timezone.activate(tz)
        else:
            if not request.user.is_authenticated():
                # User default
                timezone.deactivate()
                return
            up = UserProfile.objects.get(user=request.user)
            tz = up.timezone
            timezone.activate(tz)

            request.session['timezone'] = tz
