from django.core.management.base import BaseCommand
from apps.requests.models import Request, ViewableLink
from apps.agency.models import Agency
from apps.government.models import Government 
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

        objects = {
            'requests': [],
            'governments': [],
            'agencies': [],
            'contacts': []
        }

        writer = UnicodeWriter(open('stats/requests.csv', 'wb'))
        header = [
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
        ]
        writer.writerow(header)

        requests = list(Request.objects.all())
        for i, request in enumerate(requests):
            mb = MailBox.objects.filter(usr=request.author)
            if mb.count() < 1:
                pass
            else:
                print "Request num %s of %s" % (i, len(requests))
                mb = mb[0]
                threads = mb.get_threads(request.id)
                row = [
                    str(request.id),
                    ("" if request.agency is None else str(request.agency.id)),
                    request.get_status,
                    str(request.date_added),
                    str(request.scheduled_send_date),
                    str(request.due_date),
                    str(request.date_fulfilled),
                    str(request.private),
                    str(len(threads)),
                    ",".join([str(contact.id) for contact in request.contacts.all()])
                ]
                writer.writerow(row)
                obj = {}
                for i, key in enumerate(header):
                    obj[key] = row[i]
                objects['requests'].append(obj)

        writer = UnicodeWriter(open('stats/governments.csv', 'wb'))
        header = [
            'id',
            'name',
            'slug',
            'created',
            'agencies'
        ]
        writer.writerow(header)
        for gov in Government.objects.all():
            row = [
                str(gov.id),
                gov.name,
                gov.slug,
                str(gov.created),
                str(Agency.objects.filter(government=gov).count())
            ]
            writer.writerow(row)
            obj = {}
            for i, key in enumerate(header):
                obj[key] = row[i]
            objects['governments'].append(obj)

        writer = UnicodeWriter(open('stats/agencies.csv', 'wb'))
        header = [
            'id',
            'government_id',
            'name',
            'slug',
            'created',
            'contacts'
        ]
        writer.writerow(header)
        for agency in Agency.objects.all():
            row = [
                str(agency.id),
                str(agency.government.id),
                agency.name,
                agency.slug,
                str(agency.created),
                str(agency.contacts.all().count())
            ]
            writer.writerow(row)
            obj = {}
            for i, key in enumerate(header):
                obj[key] = row[i]
            objects['agencies'].append(obj)

        writer = UnicodeWriter(open('stats/contacts.csv', 'wb'))
        header = [
            'id',
            'agency_id',
            'first_name',
            'last_name',
            'created',
            'address',
            'phone',
            'emails'
        ]
        writer.writerow(header)

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
                obj = {}
                for i, key in enumerate(header):
                    obj[key] = row[i]
                objects['contacts'].append(obj)

        with open("stats/data.json", "w") as out:
            out.write(json.dumps(objects))