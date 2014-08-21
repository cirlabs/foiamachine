from django.conf.urls.defaults import *
from apps.mail.views import MailRequestListView, MailBoxMailListView, MailDetailView, associate_message, s3_file_view
from django.contrib.auth.decorators import login_required


urlpatterns = patterns('',
    url(r'^incoming/$', 'apps.mail.views.new_msg', name='new_msg'),
    url(r'^check/$', 'apps.mail.views.check_mail', name='check_mail'),
    url(r'^mailbox/$', login_required(MailBoxMailListView.as_view()), name='mailbox_mail_view'),
    url(r'^orphaned/$', associate_message, name='orphaned_mail_view'),
    url(r'^orphaned/(?P<message_id>.+)/$', associate_message, name='orphaned_mail_view'),
    url(r'^detail/(?P<slug>.+)/$', login_required(MailDetailView.as_view()), name='mail_detail_view'),
    url(r'^request/(?P<slug>.+)/$', login_required(MailRequestListView.as_view()), name='request_mail_view'),
    url(r'^attachments/(?P<rpk>[\d]+)/(?P<pk>[\d]+)/$', s3_file_view, name='get_attachment_view'),
)
