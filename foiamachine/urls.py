from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth.decorators import login_required

from apps.users.forms import UserRegistrationForm, UsernameOrEmailAuthenticationForm
from registration.views import register
from django.views.generic.simple import direct_to_template
from tastypie.api import Api
from apps.requests.api import RequestResource, AgencyStatsResource, UserStatsResource, ViewableLinkResource
from apps.contacts.api import ContactResource
from apps.agency.api import AgencyResource
from apps.government.api import GovernmentResource, StatuteResource, FeeExemptionResource
from apps.users.api import GroupResource, UserResource, TagResource
from apps.mail.api import MessageResource

from apps.mail.views import attachment_upload
from apps.users.views import done_registered_fp, update_or_register, how_it_works, VerifySendView, VerifyConfirmView, confirm_email, groups_view
from apps.requests.views import UserRequestListView, overall_stats
from apps.core.views import about_view

import pytz


v1_api = Api(api_name='v1')
v1_api.register(RequestResource())
v1_api.register(ContactResource())
v1_api.register(TagResource())
v1_api.register(AgencyResource())
v1_api.register(GovernmentResource())
v1_api.register(GroupResource())
v1_api.register(UserResource())
v1_api.register(AgencyStatsResource())
v1_api.register(UserStatsResource())
v1_api.register(FeeExemptionResource())
v1_api.register(ViewableLinkResource())
v1_api.register(StatuteResource())
v1_api.register(MessageResource())

admin.autodiscover()

urlpatterns = patterns('',
    # Simple login for securing site on Heroku
    #(r'^/$', 'apps.users.views.register_complete'),#change me

    # Logging in
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'authentication_form' :UsernameOrEmailAuthenticationForm}, name='login', ),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),
    url(r'^accounts/register/$', register,\
        {'backend': 'apps.users.regbackend.AuthorizeBackend',\
        'form_class': UserRegistrationForm, 'success_url': '/'}, name='registration_register'),
    url(r'^accounts/update/', update_or_register, name='account_update'),
    url(r'^accounts/verify/send/$', VerifySendView),
    url(r'^accounts/confirm-email/$', confirm_email, name="confirm_email"),
    url(r'^accounts/verify/confirm/(?P<email>.+)/$', VerifyConfirmView),
    url(r'^accounts/', include('registration.backends.simple.urls')),

    # Groups

    url(r'^groups/', groups_view, name="manage_groups"),
    # Admin
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', admin.site.urls),
    url(r'^tag_suggest/', include('taggit_autosuggest.urls')),

    # Project URLs go here
    (r'^api/', include(v1_api.urls)),

    (r'^governments/', include('apps.government.urls')),
    (r'^requests/', include('apps.requests.urls')),
    (r'^agencies/', include('apps.agency.urls')),
    (r'^docs/', include('apps.doccloud.urls')),
    (r'^mail/', include('apps.mail.urls')),

    # Temp placeholder URLs
    url(r'^community/', direct_to_template, {'template': 'shame.html'}, name='wall_of_shame'),
    url(r'^kickstarter/', direct_to_template, {'template': 'kickstarter.html'}, name='kickstarter'),
    url(r'^how-it-works/', how_it_works, name='the_workings'),
    url(r'^wiki/', about_view, name='wiki'),
    url(r'^about/', about_view, name='about'),

    # Handrolled API URLs
    url(r'api/v1/overallstats/$', overall_stats, name="overallstats"),
    url(r'api/v1/mail/attachment/$', attachment_upload, name="attachment_upload"),
)

if settings.VET_REGISTRATION:
    urlpatterns += patterns('',
        url(r'^$', done_registered_fp, name="front_page"),
        url(r'^accounts/interested/$', direct_to_template, {'template': 'registration/register_interest_thanks.html'}, name='interested_thanks'),
    )
else:
    #urlpatterns += patterns('', url(r'^$', direct_to_template, {'template': 'index.html'}, name='front_page'))
    urlpatterns += patterns('',
        url(r'^$', done_registered_fp, name="front_page"),
    )
urlpatterns += staticfiles_urlpatterns()
