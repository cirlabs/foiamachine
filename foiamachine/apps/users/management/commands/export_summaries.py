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
        writer_m = UnicodeWriter(open('stats/mail-messages.csv', 'wb'))

        writer_m.writerow([
            "id",
            "request_id",
            "sent_by",
            "dated",#when the message was sent by us
            "created",#when the message hit our db, is the same as dated if sent by us
            "direction",#sent or received
            "was_forward_by_user",#if the user forwarded a thread to associate with this request
            "is_user_note",
            "sent_to"#one or more
        ])
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
                    str(request.keep_private),
                    str(len(threads)),
                    ",".join([str(contact.id) for contact in request.contacts.all()])
                ]
                writer.writerow(row)

                for thread in threads:
                    row = [
                        str(thread.id),
                        str(request.id),
                        str(thread.email_from),
                        str(thread.dated),
                        str(thread.created),
                        str(thread.direction),
                        str(thread.was_fwded),
                        str(thread.message_id is None),
                        str(",".join(thread.get_to_emails))
                    ]
                    writer_m.writerow(row)


        writer = UnicodeWriter(open('stats/governments.csv', 'wb'))
        writer.writerow([
            'id',
            'name',
            'slug',
            'created',
            'agencies'
        ])
        for gov in Government.objects.all():
            row = [
                str(gov.id),
                gov.name,
                gov.slug,
                str(gov.created),
                str(Agency.objects.filter(government=gov).count())
            ]
            writer.writerow(row)

        writer = UnicodeWriter(open('stats/agencies.csv', 'wb'))
        writer.writerow([
            'id',
            'government_id'
            'name',
            'slug',
            'created',
            'contacts'
        ])
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