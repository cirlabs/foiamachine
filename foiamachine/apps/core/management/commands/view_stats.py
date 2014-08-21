#!/usr/bin/python

import hotshot.stats
import sys

from django.core.management.base import BaseCommand
from apps.contacts.utils import create_test_contacts, update_federal_contacts, update_california_contacts
from apps.requests.utils import populate_record_types
from apps.government.utils import load_statutes


class Command(BaseCommand):

    def handle(self, *args, **options):

        stats = hotshot.stats.load(args[0])
        #stats.strip_dirs()
        stats.sort_stats('time', 'calls')
        stats.print_stats(20)