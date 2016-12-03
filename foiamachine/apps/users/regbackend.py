from django.template.defaultfilters import slugify
from django.conf import settings
from django.utils import timezone

from apps.users.models import UserProfile, Organization
from apps.users.forms import UserRegistrationForm
from apps.users.models import InterestedParty
from apps.mail.models import MailBox
from apps.users.utils import send_verification_email

from registration.backends.simple import SimpleBackend

from datetime import datetime

import logging

logger = logging.getLogger('default')


class AuthorizeBackend(SimpleBackend):

    def registration_allowed(self, request):
        """
        Indicate whether account registration is currently permitted,
        based on the value of the setting ``REGISTRATION_OPEN``. This
        is determined as follows:

        * If ``REGISTRATION_OPEN`` is not specified in settings, or is
          set to ``True``, registration is permitted.

        * If ``REGISTRATION_OPEN`` is both specified and set to
          ``False``, registration is not permitted.
        
        """
        if settings.VET_REGISTRATION:
            #do some test
            referrer_email = request.GET.get('referringemail', '')
            activation_code = request.GET.get('activationcode', '')
            logger.info("%s %s" % (referrer_email, activation_code))
            if InterestedParty.objects.filter(activation_key__key=activation_code).count() == 1:
                ip = InterestedParty.objects.get(activation_key__key=activation_code)
                request.session['interested_party'] = ip
                return True
            if 'interested_party' in request.session.keys():
                return True
            return False
        return False

def user_created(sender, user, request, **kwargs):
    try:
        form = UserRegistrationForm(request.POST)
        #name = form.data['organization']
        is_journalist = False
        try:
            is_journalist = form.data['journalist']
        except KeyError:
            logger.info('user %s not a journalist' % user.username)
        logger.info('user %s a journalist? %s' % (user.username, is_journalist))
        
        userprofile, created = UserProfile.objects.get_or_create(user=user)
        userprofile.mailing_address = form.data['mailing_address']
        userprofile.mailing_city = form.data['mailing_city']
        userprofile.mailing_state = form.data['mailing_state']
        userprofile.mailing_zip = form.data['mailing_zip']
        userprofile.phone = form.data['phone']
        userprofile.timezone = form.data['timezone']
        userprofile.is_journalist = is_journalist
        user.first_name = form.data['first_name']
        user.last_name = form.data['last_name']

        if 'interested_party' in request.session.keys():
            request.session['interested_party'].activated_on = timezone.now()
            request.session['interested_party'].save()
            if request.session['interested_party'].email == request.user.email:
                logger.info("user %s used a verified email address" % request.user.email)
                userprofile.is_verified = True
        #until post nicar2014 verify everyone as we are only sending invites
        userprofile.is_verified = True 
        user.save()
        userprofile.save()

        #org_slug = slugify(name)
        #user_org, org_created = Organization.objects.get_or_create(slug=org_slug)
        #if org_created:
        #    userprofile.organizations.add(user_org)
        #userprofile.save()
        mailbox, created = MailBox.objects.get_or_create(usr=user)
        send_verification_email(user)
    except Exception as e:
        logger.exception(e)

from registration.signals import user_registered
user_registered.connect(user_created)
