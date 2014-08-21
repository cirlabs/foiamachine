from django.core.management.base import BaseCommand, CommandError
from django.core.mail import EmailMultiAlternatives
from apps.users.models import InterestedParty, ActivationKeyValue
from django.template.loader import get_template
from django.contrib.sites.models import Site
from django.template import Context
from django.conf import settings
from datetime import datetime
import os
import os.path
import logging
import csv

logger = logging.getLogger('default')


class Command(BaseCommand):

    def handle(self, *args, **options):
        current_site = Site.objects.get_current()
        activation_url = "https://www." + current_site.domain + '/accounts/register/'
        email_subject = 'Welcome to the FOIAMachine beta test!'
        email_from = 'admin@foiamachine.org'
        parties = InterestedParty.objects.filter(activation_key=None, created__gte=datetime(2014, 02, 26))
        if len(args) > 0:
            #whitelist file location
            #one column containing email addresses to use, no header
            reader = list(csv.reader(file(args[0], 'rb')))
            reader = map(lambda x: x[0], reader)
            parties = filter(lambda x: x.email in reader, parties)
        print parties
        print 'double check the parties before you continue, url=%s' % activation_url
        print settings.DATABASES
        import pdb;pdb.set_trace()
        plaintext = get_template('registration/activate_user.txt')
        for party in parties:
            try:
                logger.debug("creating email for interested party %s" % party.name)
                activation_key = os.urandom(10).encode('hex')
                akv, created = ActivationKeyValue.objects.get_or_create(key=activation_key)

                while not created:
                    akv, created = ActivationKeyValue.objects.get_or_create(key=activation_key)

                logger.debug("created activation key %s" % activation_key)

                party.activation_key = akv
                party.save()
                email_message_link = "%s?activationcode=%s" % (activation_url, activation_key)
                d = Context({ 'activation_link': email_message_link, 'name': party.name})
                text_content = plaintext.render(d)
                msg = EmailMultiAlternatives(email_subject, text_content, email_from, [str(party.email), 'info@foiamachine.org'])
                msg.send()
            except Exception as e:
                logger.exception(e)
