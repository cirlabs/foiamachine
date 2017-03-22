from django.core.management.base import BaseCommand, CommandError
from django.core.mail import EmailMultiAlternatives
from apps.users.models import InterestedParty, ActivationKeyValue
from django.template.loader import get_template
from django.contrib.sites.models import Site
from django.template import Context
from django.conf import settings
from django.contrib.auth.models import User, Group

import os
import os.path
import logging
import csv

logger = logging.getLogger('default')


class Command(BaseCommand):

    def handle(self, *args, **options):
        email_subject = 'Redesign Reminder'
        email_from = 'info@foiamachine.org'
        emails = ['shane.shifflett@dowjones.com', 'coulter.jones@wsj.com']
        users = User.objects.all()
        users = users.filter(email__in=emails)
        print 'users =%s' % users.count()
        print 'double check the parties before you continue' 
        print settings.DATABASES
        import pdb;pdb.set_trace()
        plaintext = get_template('registration/email/final.txt')
        htmltext = get_template('registration/email/final.html')
        for user in users:
            try:
                email_message_link = "https://docs.google.com/forms/d/1v2JGkQ6MX8DMCMUuwDhKo6KBho_FUL7AdFxIBR6j0So/viewform"
                d = Context({ 'survey_link': email_message_link, 'name': user.first_name})
                text_content = plaintext.render(d)
                html_content = htmltext.render(d)
                msg = EmailMultiAlternatives(email_subject, text_content, email_from, [str(user.email), 'info@foiamachine.org'])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
            except Exception as e:
                logger.exception(e)

