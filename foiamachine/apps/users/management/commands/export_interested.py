from django.core.management.base import BaseCommand
from apps.users.models import InterestedParty
from datetime import datetime
from apps.core.unicode_csv import UnicodeWriter
import logging
import csv

logger = logging.getLogger('default')


class Command(BaseCommand):

    def handle(self, *args, **options):
        writer = UnicodeWriter(open('interesed-parties-%s.csv' % datetime.now().date(), 'wb'))
        parties = InterestedParty.objects.all()
        if len(args) > 0:
            #whitelist file location
            #one column containing email addresses to use, no header
            reader = list(csv.reader(file(args[0], 'rb')))
            reader = map(lambda x: x[0], reader)
            parties = filter(lambda x: x.email in reader, parties)
        print len(parties)
        headers = ['first_name', 'last_name', 'email', 'activation_key', 'activated_on', 'interested_in']
        writer.writerow(headers)
        interests = {}
        for party in parties:
            row = [party.first_name, party.last_name, party.email, '' if party.activation_key == None else party.activation_key.key, str(party.activated_on), '']
            writer.writerow(row)
