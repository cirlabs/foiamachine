from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from apps.users.models import UserProfile
from apps.requests.models import Request
from django.contrib.auth.models import User, Group
import os
import os.path
import logging
import csv

from guardian.shortcuts import assign_perm, get_perms

from django.contrib.auth.models import User, Group


logger = logging.getLogger('default')


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = ['shaneshifflett', 'crondino']
        requests = [1317]
        for usr in users:
            group = Group.objects.get(name=usr)
            user = User.objects.get(username=usr)
            for rqst in requests:
                request = Request.objects.get(id=rqst)
                print "%s \t REQUEST=%s USER=%s \t CREATOR=%s" % (get_perms(group, request), request.title, user, request.author)