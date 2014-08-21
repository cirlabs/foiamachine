from django.core.management.base import BaseCommand
from apps.agency.models import Agency


import logging

logger = logging.getLogger('default')


class Command(BaseCommand):

    def handle(self, *args, **options):
        for agency in Agency.objects.all():
            agency.save()
            print agency.id