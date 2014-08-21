from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from apps.users.models import UserProfile
import os
import os.path
import logging
import csv

from guardian.shortcuts import assign_perm

from django.contrib.auth.models import User, Group


logger = logging.getLogger('default')


class Command(BaseCommand):

    def handle(self, *args, **options):
        excluded = ['public', 'AnonymousUser']
        for user in User.objects.all():
            group = Group.objects.get(name=user.username)
            assign_perm(UserProfile.get_permission_name('edit'), user, group)
            print '1 set %s %s' % (group.name, user.username)
        #retroactive support for editing permissions on groups
        #make everyone an editor of the group because we can't track who created the group
        for group in Group.objects.all().exclude(name__in=excluded):
            for user in group.user_set.all():
                assign_perm(UserProfile.get_permission_name('edit'), user, group)
                assign_perm(UserProfile.get_permission_name('view'), user, group)
                print '2 set %s %s' % (group.name, user.username)
