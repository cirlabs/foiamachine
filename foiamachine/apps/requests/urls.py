from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template
from django.views.generic import RedirectView

from .views import UserRequestListView, RequestDetailView,\
    SingleGroupRequestListView, GroupRequestListView, RequestListViewPublic, request_add_support,\
    PUBLIC_FORMS, show_pubprivate_form, new_new_request,\
    free_request_edit, send_request, disallow_sunset, send_limit, overall_stats,\
    LinkUserRequestListView,LinkRequestDetailView
from .forms import PubPrivateForm, GovernmentForm

urlpatterns = patterns('',
    url(r'send-limit/$', send_limit, name="request_send_limit"),
    url(r'my/$', login_required(UserRequestListView.as_view()), name="request_list"),
    url(r'link/(?P<pk>.+)/$', LinkRequestDetailView.as_view(), name="link_request_detail"),
    url(r'link/$', LinkUserRequestListView.as_view(), name="user_request_list"),
    url(r'group/$', login_required(GroupRequestListView.as_view()), name="request_list_group"),
    url(r'group/(?P<pk>.+)/$', login_required(SingleGroupRequestListView.as_view()), name="request_list_single_group"),
    url(r'public/$', RequestListViewPublic.as_view(), name="request_list_public"),
    url(r'new/$', new_new_request, name='request_new',),
    url(r'send/(?P<pk>.+)/$', send_request, name="send_request"),
    url(r'privacy/(?P<pk>.+)/$', disallow_sunset, name="private"),
    url(r'free-form/(?P<pk>.+)/$', free_request_edit, name='free_request_edit'),
    url(r'free-form/$', free_request_edit, name='free_request_edit'),
    url(r'stats/$', direct_to_template, {'template' : 'requests/stats.html'}, name="request_stats"),
    url(r'embed/$', direct_to_template, {'template' : 'requests/embed_generator.html'}, name="embed_generator"),
    url(r'add-support/(?P<pk>.+)/user/(?P<user_id>.+)$', request_add_support, name="request_add_support"),
    url(r'(?P<pk>.+)/$', RequestDetailView.as_view(), name="request_detail"),

    #original hackday urls
    #url(r'new-backbone/', direct_to_template, {'template': 'requests/backbone.html'}, name='request_new_backbone'),

)