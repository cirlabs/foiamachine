from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from apps.requests.models import Request
import logging
from datetime import datetime
import os
import pytz
import workdays

logger = logging.getLogger('default')
class Command(BaseCommand):
    def handle(self, *args, **options):
        # Increment days outstanding for requests not rejected/fulfilled
        therequests = Request.objects.filter(status__in=['S','R','P'])
        now = datetime.now(tz=pytz.utc)


        for request in therequests:
            try: 
                last_contact_date = request.last_contact_date
                holidays = request.government.get_holiday_dates

                if not last_contact_date and request.scheduled_send_date:
                    # Just use the send date as last_contact_date if we don't have one set
                    last_contact_date = request.last_contact_date = request.scheduled_send_date
                request.days_outstanding = workdays.networkdays(last_contact_date, now, holidays)

                request.save()
            except Exception as e:
                logger.error(e)
