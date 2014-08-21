from django.core.management.base import BaseCommand
from django.conf import settings
from apps.supporters.models import SupportLevel, Supporter
import os
import glob
import csv
import re


class Command(BaseCommand):

    def handle(self, *args, **options):
        csv_dir = os.path.join(settings.SITE_ROOT, 'apps/supporters/data')
        Supporter.objects.all().delete()
        for filename in glob.glob('%s/*.csv' % (csv_dir,)):
            print filename
            csv_file = open(filename)
            handle = csv.DictReader(csv_file)

            for hnd in handle:
                donation = re.sub('[$,USD ]', '', hnd['Pledge Amount'].strip())

                correct_level = None
                for sl in SupportLevel.objects.all().order_by('minimum_amount'):
                    if float(donation) >= sl.minimum_amount:
                        correct_level = sl
                print '%s: %s' % (donation, correct_level,)

                supporter, created = Supporter.objects.get_or_create(
                    kickstarter_id=hnd['\xef\xbb\xbfBacker Id'],
                    name=hnd['Backer Name'].strip(),
                    support_level=correct_level
                )
