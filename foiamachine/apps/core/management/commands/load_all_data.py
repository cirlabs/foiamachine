from django.core.management.base import BaseCommand
from apps.contacts.utils import create_test_contacts, update_federal_contacts, update_california_contacts
from apps.requests.utils import populate_record_types
from apps.government.utils import load_statutes, load_states


class Command(BaseCommand):

    def handle(self, *args, **options):
        #update_california_contacts()
        #update_federal_contacts()
        create_test_contacts()
        populate_record_types()
        load_statutes()
        load_states()
