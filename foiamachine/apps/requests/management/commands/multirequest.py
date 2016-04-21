from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group
from django.template.loader import get_template
from django.template import Context
from django.template import Template
from django.core.cache import cache
from apps.core.unicode_csv import UnicodeReader
from django.conf import settings

from apps.mail.models import MailBox
from apps.requests.models import Request
from apps.government.utils import get_defaults, get_or_create_us_govt
from apps.agency.models import Agency
from apps.contacts.models import Contact
from apps.users.models import UserProfile


from guardian.shortcuts import assign_perm, remove_perm, get_groups_with_perms


import logging
import requests
import codecs
import csv
from datetime import datetime

logger = logging.getLogger('default')

class Command(BaseCommand):
    '''
    Load contacts, agencies necessary for templated requests
    Create requests for each agency and stage them
    '''

    def handle(self, *args, **options):
        letter_responses = {}
        if len(args) < 1:
            print "Please provide ID of Google Spreadsheet"
            return -1
        idd = args[0]
        resp = requests.get("https://docs.google.com/spreadsheets/d/%s/pub?output=csv" % idd)
        reader = list(csv.reader(resp.content.split('\n'), delimiter=','))
        header = reader[0]
        for row in reader[1:-1]:
            #get user, contact and agency
            user = User.objects.get(username=row[header.index('username')])
            user_profile = UserProfile.objects.get(user=user)
            govt = get_or_create_us_govt(row[header.index("state")], 'state')
            agency, acreated = Agency.objects.get_or_create(name=row[header.index("agency")], government=govt)
            contact, ccreated = agency.contacts.get_or_create(
                first_name=row[header.index("contact.first.name")], 
                middle_name=row[header.index("contact.middle.name")], 
                last_name=row[header.index("contact.last.name")])
            if row[header.index("contact.email")] != "":
                contact.add_email(row[header.index("contact.email")])
            if row[header.index("contact.phone")] != "":
                contact.add_phone(row[header.index("contact.phone")])

            #set up group and tags
            group, created = Group.objects.get_or_create(name=row[header.index("group")])
            assign_perm(UserProfile.get_permission_name('edit'), user, group)
            assign_perm(UserProfile.get_permission_name('view'), user, group)
            user.groups.add(group)
            user_profile.tags.add(row[header.index("tag")])

            #assemble law text
            law_texts = []
            for l in govt.statutes.all():
                law_texts.append('%s' % (l.short_title,))
            law_text = ' and '.join(law_texts)

            #get the letter template
            letter_url = row[header.index("letter.url")]
            letter_template = ''
            if letter_url in letter_responses.keys():
                letter_template = letter_responses[letter_url]
            else:
                letter_resp = requests.get(letter_url)
                letter_template = letter_resp.content
                letter_responses[letter_url] = letter_template

            #render the template
            context = Context({ 
                'contact': contact, 
                'user_profile': user_profile,
                'user': user,
                'law_text': law_text
            })
            template = Template(letter_template)
            letter = template.render(context)

            #create the request
            fields_to_use = {
                'author': user,
                'title': row[header.index("request.title")],
                'free_edit_body': letter,
                'private': True if row[header.index("request.private")] == "TRUE" else False,
                'text': letter#silly distinction leftover from old days but fill it in
            }
            #delete all requests that look like the one i'm about to make so we don't have duplicates floating around
            Request.objects.filter(author=user, title=row[header.index("request.title")]).delete()
            #create the request
            therequest = Request(**fields_to_use)
            therequest.date_added = datetime.now()
            therequest.save()
            therequest.contacts = [contact]
            therequest.government = govt
            therequest.agency = agency
            therequest.tags.add(row[header.index("tag")])
            therequest.save()
            #assing permissions to the request
            assign_perm(Request.get_permission_name('view'), group, therequest)
            assign_perm(Request.get_permission_name('edit'), group, therequest)

            if row[header.index("request.send")] == "TRUE":
                therequest.send()
                print "SENT request %s" % row[header.index("request.title")]
            else:
                print "STAGED request %s" % row[header.index("request.title")]