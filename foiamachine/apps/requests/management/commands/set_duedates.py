from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from apps.requests.models import Request
import logging
from datetime import datetime
import os


class Command(BaseCommand):

    def handle(self, *args, **options):
        therequests = Request.objects.all()
        for idx, request in enumerate(therequests):
            duedate = request.get_due_date
            print idx
            #import pdb;pdb.set_trace()
