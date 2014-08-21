from django.conf.urls.defaults import *

from apps.government.views import StatuteListView, StatuteDetailView


urlpatterns = patterns('',
    url(r'statutes/(?P<pk>[0-9]+)/$', StatuteDetailView.as_view(), name="statute_detail"),
    url(r'statutes/(?P<slug>.+)/$', StatuteDetailView.as_view(), name="statute_detail"),
    url(r'statutes/$', StatuteListView.as_view(), name="statute_list"),
)
