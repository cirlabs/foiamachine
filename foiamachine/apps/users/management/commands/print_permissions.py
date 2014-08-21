from django.core.management.base import BaseCommand
from apps.users.utils import get_users_request_perms

class Command(BaseCommand):

    def handle(self, *args, **options):
        get_users_request_perms(args[0], int(args[1]))