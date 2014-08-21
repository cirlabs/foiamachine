from django.core.management.base import BaseCommand, CommandError
from django.core.mail import EmailMultiAlternatives
from apps.users.models import InterestedParty, ActivationKeyValue
from django.template.loader import get_template
from django.contrib.sites.models import Site
from django.template import Context
from apps.core.unicode_csv import UnicodeWriter

from datetime import datetime
import os
import os.path
import logging
import csv
import random

logger = logging.getLogger('default')


class Command(BaseCommand):

    def handle(self, *args, **options):
        current_site = Site.objects.get_current()
        parties = InterestedParty.objects.filter(activation_key=None)
        writer = UnicodeWriter(open('whitelist-%s.csv' % datetime.now().date(), 'wb'))
        headers = ['email']
        writer.writerow(headers)
        interests = {}
        for party in random.sample(parties, parties.count()):
            print "%s %s" % (party.first_name, party.last_name)
            row = [party.email]
            writer.writerow(row)
        print interests
