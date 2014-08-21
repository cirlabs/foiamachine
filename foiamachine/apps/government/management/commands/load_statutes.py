from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from apps.government.utils import load_statutes

class Command(BaseCommand):

    def handle(self, *args, **options):
        load_statutes()
        