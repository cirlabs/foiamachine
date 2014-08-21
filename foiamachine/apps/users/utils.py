from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import get_template
from django.template import Context
from django.contrib.auth.models import User, Group
from apps.users.models import UserProfile

from urllib2 import quote
import logging


logger = logging.getLogger('default')

def send_verification_email(user):
    "Ask a user to verify his email address"

    email_subject = "Verify address for FOIAMachine.org"
    email_body = "Please click http://foiamachine.org/accounts/verify/confirm/%s/ to verify your email address" % quote(user.email)
    email_from = 'info@foiamachine.org'

    send_mail(email_subject, email_body, email_from, [user.email], fail_silently=False)




def send_thanks(parties):
    email_subject = 'Thank you for registering for the FOIA Machine beta test!'
    email_from = 'info@foiamachine.org'
    plaintext = get_template('registration/email/registered_interest_response.txt')
    htmltext = get_template('registration/email/registered_interest_response.html')
    for party in parties:
        try:
            logger.info("sending to %s" % party.name)
            d = Context({'firstname': party.first_name, 'lastname': party.last_name})
            text_content = plaintext.render(d)
            html_content = htmltext.render(d)
            msg = EmailMultiAlternatives(email_subject, text_content, email_from, [str(party.email)])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except Exception as e:
            logger.exception(e)


def get_users_request_perms(username, request_id):
    prof = UserProfile.objects.get(user__username=username)
    print prof.get_permissions(request_id)
