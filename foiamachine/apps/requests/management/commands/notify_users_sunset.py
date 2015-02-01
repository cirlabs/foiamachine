from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from apps.requests.models import Request, Notification
import json
import logging
import requests
import settings
from datetime import datetime
import os


class Command(BaseCommand):

    def handle(self, *args, **options):
        length = settings.SUNSET_CONFIG['time']
        units = settings.SUNSET_CONFIG['units']
        days_old = length
        if units == 'months':
            days_old = days_old * 30
        if units == 'years':
            days_old = days_old * 365

        days_to_wait = settings.SUNSET_CONFIG['days_to_wait_before_action']
        therequests = Request.get_all_sunsetting(days_old - days_to_wait)

        for request in therequests:
            print "SUNSET NOTIFICATION requst %s" % request.id
            user = request.author
            address = user.email
            try:
                address = settings.TASK_EMAIL_RECIPIENT
            except:
                pass

            notifcation = Notification(type=Notification.get_type_id('Sunset clause notification'), sent=datetime.now(), request=request)
            notifcation.save()

            data = {
                "from" : "admin@foiamachine.org",
                "to" : address,
                'subject' : 'An important message regarding your request to ' + request.agency.name,
                'html' : """
                    According to our records, you sent a request to %s about %s %s ago. <br />
                    It's FOIA Machine's policy to make private requests public after %s %s if you take no further action.<br/>
                    If you do nothing your request will be made public in %s days. <br/>
                    If you'd like to keep your request private, follow this link:
                    <a href="https://www.foiamachine.org/requests/privacy/%s">https://www.foiamachine.org/requests/privacy/%s</a>
                    """ % (request.agency.name, length, units, length, units, days_to_wait, request.id, request.id)
            }

            post_url = settings.MG_POST_URL

            if settings.SEND_NOTIFICATIONS:
                resp = requests.post(
                        post_url,
                        auth=("api", settings.MAILGUN_KEY),
                        data=data)
                content = json.loads(resp.content)
                logging.info('SENT NOTIFICATION STATUS:%s' % content)
