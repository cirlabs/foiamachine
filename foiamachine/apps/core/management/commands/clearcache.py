from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache

class Command(BaseCommand):
    help = 'Clears the application cache'

    def handle(self, *args, **options):
        try:
            cache.clear()
            self.stdout.write('Successfully cleared cache\n')
        except AttributeError:
            raise
