from apps.requests.utils import populate_record_types

from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache

class Command(BaseCommand):

    def handle(self, *args, **options):
        populate_record_types()