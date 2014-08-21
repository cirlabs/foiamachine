from django.core.management.base import BaseCommand
from apps.contacts.utils import update_federal_contacts,\
    create_test_contacts, update_california_contacts, create_msmith_contacts,\
    create_mdrange_contacts

from apps.contacts.models import Contact
from apps.agency.models import Agency
from taggit.models import Tag


import logging

logger = logging.getLogger('default')


class Command(BaseCommand):

    def handle(self, *args, **options):
        #Agency.objects.all().delete()
        #Contact.objects.all().delete()
        #print 'deleted agencies and contacts'
        #california contacts are shit, needs to be manually paired down before loading
        #update_california_contacts()
        Tag.objects.all().delete()
        print 'deleted tags'
        #update_federal_contacts()
        #print 'loaded new federal contacts'
        create_test_contacts()
        print 'created test contacts'
        #create_msmith_contacts()
        #print 'create msmith contacts'
        #create_mdrange_contacts()
        #print 'created mdrange contacts'
