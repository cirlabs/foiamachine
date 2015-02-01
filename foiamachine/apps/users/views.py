from django.forms.models import inlineformset_factory, modelform_factory
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import timezone
from django.conf import settings
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import TemplateView
from django import forms


from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required

from apps.users.models import InterestedParty, UserProfile
from apps.mail.models import MailBox
from apps.users.utils import send_verification_email
from apps.users.forms import InterestedPartyForm 
from apps.requests.views import UserRequestListView

import copy
import pytz

import logging

logger = logging.getLogger('default')


def register_complete(request, template_name='registration/registration_complete.html'):
    context = {}   
    return render_to_response(template_name, context, context_instance=RequestContext(request))


def how_it_works(request, template_name='how-it-works.html'):
    context = {}
    context['sunset_unit'] = settings.SUNSET_CONFIG['units']
    context['sunset_time'] = settings.SUNSET_CONFIG['time']
    if request.user.is_authenticated():
        context['provisioned_email'] = MailBox.objects.get(usr=request.user).get_provisioned_email()
    else:
        context['provisioned_email'] = 'EMAIL UNAVAILABLE'
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def confirm_email(request, template_name='users/confirm_email.html'):
    context = {}
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def done_registered_fp(request):
    if not request.user.is_authenticated():
        rv = RegisterInterestView.as_view()
        return rv(request)
    rv = UserRequestListView.as_view()
    return rv(request)

def update_or_register(request):
    if not request.user.is_authenticated():
        rv = RegisterInterestView.as_view()
        return rv(request)

    oldemail = copy.copy(request.user.email)
    # Need to allow user to edit fields in profile and user object
    userprofile_fields = ['mailing_address', 'mailing_state', 'mailing_city', 'mailing_zip', 'phone', 'timezone']
    user_fields = ['email']

    userprofile_form_factory = modelform_factory(UserProfile, fields = userprofile_fields)
    user_form_factory = modelform_factory(User, fields = user_fields) 
    up = UserProfile.objects.get(user=request.user)
    verified = up.is_verified
    updated = False

    if request.method == 'POST':
        user_form = user_form_factory(request.POST, instance=request.user)
            
        userprofile_form = userprofile_form_factory(request.POST, instance=up)
        if user_form.is_valid() and userprofile_form.is_valid():
            email_changed = (oldemail != user_form.cleaned_data['email'])
            if email_changed and User.objects.filter(email=user_form.cleaned_data['email']).count() > 0:
                logger.error("User %s tried to change email using another user's email=%s" % (request.user.username, user_form.cleaned_data['email']))
                #TODO deal with this VE in the template
                user_form.errors["email"] = "This email is already associated with another user!"
            else:
                user_form.save()
                userprofile_form.save()
                request.session['timezone'] = userprofile_form.cleaned_data['timezone']
                timezone.activate(request.session['timezone'])
                updated = True
                if email_changed:
                    # If the email address changed, flag as not verified
                    up = UserProfile.objects.get(user=request.user)
                    up.is_verified = False
                    verified = False
                    up.save()
                    send_verification_email(request.user)
    else:
        user_form = user_form_factory(instance=request.user)
        userprofile_form = userprofile_form_factory(instance=up)
    zones = pytz.common_timezones
    zones = [z for z in zones if z.startswith('US')] + [z for z in zones if not z.startswith('US')]
    return render_to_response('users/userprofile_form.html', {'timezones' : zones, 'updated' : updated, 'user_form' : user_form, 'userprofile_form' : userprofile_form, 'verified' : verified}, context_instance=RequestContext(request))


@login_required
def groups_view(request, template="users/groups.html"):
    context = {}
    return render_to_response(template, context, context_instance=RequestContext(request))

@login_required
def VerifySendView(request):
    template_name = "users/verify_send.html"
    context = {}   
    send_verification_email(request.user)
    return render_to_response(template_name, context, context_instance=RequestContext(request))

def VerifyConfirmView(request, email):
    template_name = 'users/verify_confirm.html'
    context = {}   
    context['success'] = False

    try: 
        up = UserProfile.objects.get(user__email=email)
        context['success'] = True
        up.is_verified = True
        up.save()
    except Exception as e:
        logger.error("Error finding user with email %s e=%s" % (email, e))
        pass
        

    return render_to_response(template_name, context, context_instance=RequestContext(request))

      
class RegisterInterestView(CreateView):
    template_name = 'registration/register_interest.html'
    model = InterestedParty
    success_url = 'accounts/interested'
    form_class = InterestedPartyForm

    def form_valid(self, form):
        return super(RegisterInterestView, self).form_valid(form)
