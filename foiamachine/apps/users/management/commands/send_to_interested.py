from django.core.management.base import BaseCommand, CommandError
from django.core.mail import EmailMultiAlternatives
from apps.users.models import InterestedParty, ActivationKeyValue
from django.template.loader import get_template
from django.contrib.sites.models import Site
from django.template import Context
from datetime import datetime
import os
import os.path
import logging
import csv

logger = logging.getLogger('default')


class Command(BaseCommand):

    def handle(self, *args, **options):
        current_site = Site.objects.get_current()
        #activation_url = current_site.domain + '/accounts/register/'
        email_subject = 'TEST FOIA Machine: The last push'
        email_from = 'info@foiamachine.org'
        parties = InterestedParty.objects.all().order_by("id")
        if len(args) > 0:
            #whitelist file location
            #one column containing email addresses to use, no header
            reader = list(csv.reader(file(args[0], 'rb')))
            reader = map(lambda x: x[0], reader)
            parties = filter(lambda x: x.email in reader, parties)
        print parties
        print 'double check the parties before you continue'
        import pdb;pdb.set_trace()
        plaintext = get_template('registration/email/kickstarter.txt')
        print plaintext
        htmltext = get_template('registration/email/kickstarter.html')
        for party in parties:
            try:
                print "sending to %s %s" % (party.name, party.id)
                d = Context({ 'firstname': party.first_name, 'lastname': party.last_name })
                text_content = plaintext.render(d)
                html_content = htmltext.render(d)
                msg = EmailMultiAlternatives(email_subject, text_content, email_from, [str(party.email)])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
            except Exception as e:
                logger.exception(e)
                print e