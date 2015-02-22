from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from django.conf import settings
from apps.government.models import *
import json
import os


class Command(BaseCommand):

    def handle(self, *args, **options):
        objs = {}
        for statute in Statute.objects.all():
            obj = {
                'short_title': statute.short_title,
                'designator': statute.designator,
                'days_till_due': statute.days_till_due,
                'slug': statute.slug,
            }
            objs[statute.slug] = obj
        filename = os.path.join(settings.SITE_ROOT, 'assets/js/statutes.json')
        with open(filename, "w") as out:
            out.write("var statutes = " + json.dumps(objs))
