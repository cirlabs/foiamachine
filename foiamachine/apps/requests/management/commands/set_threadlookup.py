from apps.requests.models import Request

from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from apps.users.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):

        for rr in Request.objects.all():
            code = "LOOKUP:" + User.objects.make_random_password(length=64)
            while Request.objects.filter(thread_lookup=code):
                code = User.objects.make_random_password(length=64)
            rr.thread_lookup = code
            rr.save()
            print 'request id=%s saved' % rr.id