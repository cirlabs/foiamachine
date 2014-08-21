from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseGone, Http404,HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, RedirectView
from apps.mail.models import MailMessage, MailBox, Attachment
from apps.requests.models import Request
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.template import RequestContext
from django import forms
from os.path import basename

from django.contrib.auth.models import User
from django.conf import settings

from boto.s3.connection import S3Connection

import logging

logger = logging.getLogger('default')

class SizeLimitedFileField(forms.FileField):
    def clean(self, *args, **kwargs):
        data = super(SizeLimitedFileField, self).clean(*args, **kwargs)

        try:
            if data.size > settings.ATTACHMENT_SIZE_LIMIT:
                raise forms.ValidationError("File too large.")
        except AttributeError:
            pass
        return data
class UploadFileForm(forms.Form):
    file = SizeLimitedFileField()

@login_required
def attachment_upload(request):
    if request.method != 'POST':
        raise Http404
    form = UploadFileForm(request.POST, request.FILES)

    if form.is_valid():
        atch = Attachment()
        atch.user = request.user
        f = request.FILES['file']
        atch.file.save(f.name, f)
        atch.save()
        return render_to_response('mail/file_upload_response.json', {"attachment": atch.id, "url": atch.url, "filename": atch.get_filename}, context_instance = RequestContext(request))
    else:
        return HttpResponseBadRequest('File too large')
        
@csrf_exempt
def new_msg(request):
    '''
    receive a new message from mailgun and store
    '''
    message, inreply = MailBox.parse_message_http(request.POST)
    messages = message.get_email_addresses()
    logger.debug('INCOMING: emails=%s files=%s' % (messages, request.FILES))
    for email in messages:
        try:
            mb = MailBox.objects.get(provisioned_email=email)\
                if MailBox.objects.filter(provisioned_email=email).count() > 0\
                else MailBox.objects.get(usr__email=email)
            logger.debug('INCOMING: found inbox for email=%s mb=%s' % (email, mb.pk))
            mb.messages.add(message)
            mb.store_message(message, inreply, request.FILES)
        except Exception as e:
            #generally just indicates we can't find the inbox
            logger.debug('incoming: email=%s exception=%s' % (email, e))
    return HttpResponse('OK')


def check_mail(request):
    mb = get_object_or_404(MailBox, usr=request.user)
    result = ''
    try:
        result = mb.check_and_save_mail()
    except Exception as e:
        logger.exception(e)
    return HttpResponse(str(result))


def setup_message_reassignment(request):
    return (Request.objects.for_user(request.user), csrf(request)['csrf_token'])


@login_required
def s3_file_view(request, rpk, pk):
    attachment = get_object_or_404(Attachment, id=pk)
    user = request.user
    therequest = get_object_or_404(Request, id=rpk)
    can_view = user.has_perm(Request.get_permission_name('view'), therequest)
    if not can_view:
        return render_to_response('403.html', {}, context_instance=RequestContext(request))
    return HttpResponseRedirect(attachment.file.url)


@login_required
def associate_message(request, message_id=None):
    context = {}
    context.update(csrf(request))
    mb = get_object_or_404(MailBox, usr=request.user)
    context['mailbox'] = mb
    template_name = 'mail/orphaned-messages-view.html'
    if request.method == 'GET':
        context['mail_messages'] = mb.get_orphaned_messages()
        requests, thecsrf = setup_message_reassignment(request)
        context['requests'] = requests
        context['csrf'] = thecsrf
    elif request.method == 'POST' and message_id is not None:
        try:
            message = MailMessage.objects.get(id=message_id)
            request_obj = Request.objects.get(id=request.POST.get('request', None))
            message.request = request_obj
            message.save()
            return redirect('request_detail', pk=request_obj.id)
        except Exception as e:
            logger.exception(e)
            context['error_msg'] = 'Could not find request or message'
    return render_to_response(template_name, context, context_instance=RequestContext(request))


class MailDetailView(DetailView):
    """
    Returns a specific request using the slug as the unique identifier
    """
    context_object_name = 'mail_message'
    template_name = 'mail/mail_detail.html'
    model = MailMessage

    def get_context_data(self, **kwargs):
        context = super(MailDetailView, self).get_context_data(**kwargs)
        mb = MailBox.objects.get_or_create(usr=self.request.user)[0]
        threads = mb.get_threads()
        context['replies'] = threads[0] if len(threads) > 0 else None
        context['mailbox'] = mb
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MailDetailView, self).dispatch(*args, **kwargs)


class MailRequestListView(ListView):
    """
    Main view showing the list of all user's requests. Used as an index page.
    """
    template_name = 'mail/mail_request_list.html'
    context_object_name = 'mail_messages'

    def get_queryset(self):
        objs = MailMessage.objects.filter(request__slug=self.kwargs['slug'])
        return objs

    def get_context_data(self, **kwargs):
        context = super(MailRequestListView, self).get_context_data(**kwargs)
        mb = MailBox.objects.get_or_create(usr=self.request.user)[0]
        threads = mb.get_threads()
        context['replies'] = threads[0] if len(threads) > 0 else None
        context['mailbox'] = mb
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MailRequestListView, self).dispatch(*args, **kwargs)


class MailBoxMailListView(ListView):
    """
    Main view showing the list of all user's requests. Used as an index page.
    """
    context_object_name = 'mail_messages'
    template_name = 'mail/mail_request_list.html'

    def get_queryset(self):
        return MailBox.objects.get(usr=self.request.user).messages.all()

    def get_context_data(self, **kwargs):
        context = super(MailBoxMailListView, self).get_context_data(**kwargs)
        context['mailbox'] = MailBox.objects.get_or_create(usr=self.request.user)[0]
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MailBoxMailListView, self).dispatch(*args, **kwargs)
