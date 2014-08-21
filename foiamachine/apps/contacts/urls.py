from django.conf.urls.defaults import *

from apps.contacts.views import create_contact

urlpatterns = patterns('',
    url(r'^create/$', create_contact, name='create_contact_view'),
)
