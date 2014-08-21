from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
from .views import AgencyListView, AgencyDetailView


urlpatterns = patterns('',
    url(r'detail/(?P<slug>.+)/$', AgencyDetailView.as_view(), name="agency_detail"),
    url(r'^$', login_required(AgencyListView.as_view()), name="agency_list"),
)
