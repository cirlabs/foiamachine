from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group
from apps.mail.models import MailBox
from django.core.cache import cache
from apps.requests.models import Request
import logging
from datetime import datetime
import os
import pytz
import workdays

logger = logging.getLogger('default')
class Command(BaseCommand):
    '''
    Find messages and set the stats where someone responded who was part of the initial request 
    '''
    def handle(self, *args, **options):
        therequests = Request.objects.filter(government__isnull=False)
        for req in therequests.filter(status__in=['R','P','F']):
            mb = MailBox.objects.get(usr=req.author)
            messages = mb.get_threads(req.id)
            contacts = req.contacts.all()
            for msg in messages:
                for contact in contacts:
                    for email in contact.emails.all():
                        if(msg.email_from == email.content):
                            holidays = req.government.get_holiday_dates
                            req.first_response_time = workdays.networkdays(req.scheduled_send_date, msg.dated, holidays)
                            req.save()
                            print "HERE %s %s %s" % (msg.email_from, msg.dated, req.first_response_time)
                            '''
                            TODO
                            add logic to find the last contact date
                            set whether it was overdue
                            add UI element to mark a message as the agency's response
                                (how would this work bc users can forward a message so the date needs to be accurately counted)
                                add a UI field for date input, so you can scroll down to the message click mark this and add the date of the response
                            add UI element to mark a request as part of the official stats
                                can we use groups instead of a flag? that way we can do periodic studies to see how things improve / degrade...
                                would need more of an admin interaface to create a stats group, add requests to it and view stats by group
                            '''

        for req in therequests.filter(status__in=['F']).filter(scheduled_send_date__isnull=False):
            now = datetime.now(tz=pytz.utc)
            holidays = req.government.get_holiday_dates
            req.lifetime = workdays.networkdays(req.scheduled_send_date, now, holidays)
            req.save()

