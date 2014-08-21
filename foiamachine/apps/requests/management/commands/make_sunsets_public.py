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
        therequests = Request.get_sunsetted(days_old)
        for request in therequests:
            request.private = False
            #don't put user in a loop if they don't follow teh email link to set this flag
            #if we don't set it adn the user makes the request private after we make it public
            #it will become public again when this script runs
            request.keep_private = True
            request.save()
            print request.id