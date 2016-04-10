from django.core.management.base import BaseCommand
from apps.requests.models import Request, ViewableLink
from apps.agency.models import Agency
from apps.contacts.models import Contact
from apps.core.unicode_csv import UnicodeWriter
from apps.mail.models import MailMessage, MailBox
from datetime import datetime
import os
import os.path
import logging
import csv
import random
import json

class Command(BaseCommand):

    def handle(self, *args, **options):
	    writer = UnicodeWriter(open('stats/requests.csv', 'wb'))
	    writer.writerow([
	    		"id",
	    		"agency_id",
	    		"status",
	    		"created",
	    		"sent",
	    		"due_date",
	    		"fullfilled_date",
	    		"private",
	    		"num_messages",
	    		"contacts"
	    	])
	    for request in Request.objects.all():
	    	mb = MailBox.objects.get(usr=request.author)
	    	row = [
	    		str(request.id),
	    		str(request.agency.id),
	    		request.get_status,
	    		str(request.created),
	    		str(request.scheduled_send_date),
	    		str(request.due_date),
	    		str(request.date_fulfilled),
	    		str(request.keep_private),
	    		str(len(mb.get_threads(request.id))),
	    		",".join([contact.id for contact in request.contacts.all()])
	    	]

    	
        writer = UnicodeWriter(open('stats/agencies.csv', 'wb'))
        writer.writerow([
        	'id',
        	'government_id'
        	'name',
        	'slug',
        	'created',
        	'contacts'
        	])
    	for agency in Agency.objects.all().exclude(name='THE TEST AGENCY'):
    		row = [
    			str(agency.id),
    			str(agency.government.id),
    			agency.name,
    			agency.slug,
    			str(agency.created),
    			str(agency.contacts.all().count())
    		]
    		writer.writerow(row)

    	writer = UnicodeWriter(open('stats/contacts.csv', 'wb'))
    	writer.writerow([
    		'id',
    		'agency_id',
    		'first_name',
    		'last_name',
    		'created',
    		'address',
    		'phone',
    		'emails'
    		])
    	for agency in Agency.objects.all():
	    	for contact in agency.contacts.all():
	    		row = [
	    			str(contact.id),
	    			str(agency.id),
	    			contact.first_name,
	    			contact.last_name,
	    			str(contact.created),
	    			("" if contact.get_first_active_address is None else contact.get_first_active_address.content),
	    			("" if contact.get_first_active_phone is None else contact.get_first_active_phone.content),
	    			("" if contact.get_first_active_email is None else contact.get_first_active_email.content)
	    		]
	    		writer.writerow(row)

