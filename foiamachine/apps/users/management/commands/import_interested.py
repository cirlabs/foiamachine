from django.core.management.base import BaseCommand
from apps.users.models import InterestedParty
from apps.core.unicode_csv import UnicodeReader
from datetime import datetime
import logging
import csv

logger = logging.getLogger('default')


class Command(BaseCommand):

    def handle(self, *args, **options):
        fname = args[0]
        reader = list(UnicodeReader(open(fname, 'rb')))
        headers = ['name', 'email', 'activation_key', 'activated_on', 'interested_in']
        for row in reader[1:]:
            try:
                ip = InterestedParty(first_name=row[0], last_name=row[1], email=row[2])
                ip.save()
            except:
                print 'dupe %s %s' % (row[0], row[1])

