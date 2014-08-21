from apps.users.models import UserProfile
from django.contrib.auth.models import User, Group

from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache

class Command(BaseCommand):

    def handle(self, *args, **options):
        for user in User.objects.all():
            try:
                up = UserProfile.objects.get(user=user)
            except Exception as e:
                print "no userprofile for %s" % user.username
                up = UserProfile(user=user)
                up.save()
