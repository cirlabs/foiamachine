from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group
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
from datetime import datetime

logger = logging.getLogger('default')
    
userconfig = {
    'shaneshifflett': {
        'name': 'Shane Shifflett',
        'username': u'shaneshifflett',
        'password': u'ncaa-project',
        'email': u'shane.shifflett@huffingtonpost.com',
        'address': u'770 Broadway',
        'city': 'New York',
        'state': 'New York',
        'zip': '10003',
        'phone': '415-323-5830'
    },
    'benhallman': {
        'name': 'Ben Hallman',
        'username': u'benhallman',
        'password': u'ncaa-project',
        'email': u'Benjamin.Hallman@huffingtonpost.com',
        'address': u'770 Broadway',
        'city': 'New York',
        'state': 'New York',
        'zip': '10003',
        'phone': '415-323-5830'
    },
    'bradwolverton': {
        'name': 'Brad Wolverton',
        'username': u'bradwolverton',
        'password': u'ncaa-project',
        'email': u'brad.wolverton@chronicle.com',
        'address': u'1255 Twenty-Third St., N.W.',
        'city': 'Washington',
        'state': 'D.C.',
        'zip': '20037',
        'phone': '202-557-8691'
    },
    'sandhyakambhampati': {
        'name': u'Sandhya Kambhampati',
        'username': u'sandhyakambhampati',
        'password': u'ncaa-project',
        'email': u'sandhya@chronicle.com',
        'address': u'1255 Twenty-Third St., N.W.',
        'city': 'Washington',
        'state': 'D.C.',
        'zip': '20037',
        'phone': '202-466-1201'
    }
   
}

ncaa_tag_name = "NCAA Expense Report"
coach_tag_name = "Coaches Contract"
ncaa_group, created = Group.objects.get_or_create(name=ncaa_tag_name)
coach_group, created = Group.objects.get_or_create(name=coach_tag_name)

def create_users():
    for key in userconfigs.keys():
        obj = userconfigs[key]
        user, c = User.objects.get_or_create(
            username=obj['shaneshifflett'],
            email=obj['email'],
        )
        user.set_password(obj['password'])
        userprofile, created = UserProfile.objects.get_or_create(user=user)
        userprofile.mailing_address = obj['address']
        userprofile.mailing_city = obj['city']
        userprofile.mailing_state = obj['state']
        userprofile.mailing_zip = obj['zip']
        userprofile.phone = obj['phone']
        userprofile.timezone = 'US/Eastern'
        userprofile.is_journalist = True
        userprofile.is_verified = True
        user.first_name = obj['name'].split(' ')[0]
        user.last_name = obj['name'].split(' ')[-1]

        user.save()
        userprofile.save()
        mailbox, created = MailBox.objects.get_or_create(usr=user)
        user.groups.add(ncaa_group)
        user.groups.add(coach_group)



class Command(BaseCommand):
    '''
    Load contacts, agencies necessary for templated requests
    Create requests for each agency and stage them
    '''
    def handle(self, *args, **options):


        users = [
            User.objects.get(username='shaneshifflett'),
            #User.objects.get(username='benhallman'),
            #User.objects.get(username='bradwolverton'),
            #User.objects.get(username='sandhyakambhampati')
        ]
        up = UserProfile.objects.get(user=users[0])
        up.tags.add(ncaa_tag_name)
        up.tags.add(coach_tag_name)
        for user in users:
            assign_perm(UserProfile.get_permission_name('edit'), user, ncaa_group)
            assign_perm(UserProfile.get_permission_name('view'), user, ncaa_group)
            assign_perm(UserProfile.get_permission_name('edit'), user, coach_group)
            assign_perm(UserProfile.get_permission_name('view'), user, coach_group)

        #Request.objects.all().delete()
        ncaa_text_to_use = """
        Pursuant to the %s, I am requesting the following documents:<br/><br/>\
        The equity/revenue-and-expenses report completed by the athletic department for the \
        National Collegiate Athletic Association for the 2014 fiscal year. This report is a \
        multi-page document that had to be submitted to the NCAA by Jan. 15, 2015. \
        It contains 38 revenue and expense categories, followed by specific breakdowns of \
        each of those categories, by sport and gender. I am requesting the full report, \
        including the detail tables and the Statement of Revenues and Expenses that appear at the end of the report. <br/><br/>\
        PLEASE NOTE: The NCAA report is different than the equity report that is sent to the\
        U.S. Department of Education for Title IX compliance. <br/><br/>\
        %s
        """

        coach_text_to_use = """
        Pursuant to %s, I am requesting the following documents:<br/><br/>\
        The current contracts for %s. If a contract is under negotiation, \
        please forward the current contract but let me know that a new contract may be forthcoming. \
        If there is no contact for one or both, please forward the letter(s) of intent or other \
        document(s) outlining each employee's conditions of employment \
        -- including bonus structure -- and/or a current statement of salary. <br/><br/>\
        %s
        """

        fname = settings.SITE_ROOT + "/apps/requests/data/NCAA-pio.csv"
        #with codecs.open(fname, 'w', encoding="utf-8") as f:
        #    resp = requests.get("https://docs.google.com/spreadsheets/d/1kccaiCCYIHOTEvpUWQiKs51v6K2TNRX7-NN6l1WtzyM/pub?output=csv")
        #    f.write(resp.text)

        reader = list(UnicodeReader(open(fname, 'rb')))
        #create contacts
        header = reader[0]
        for idx, row in enumerate(reader[1:]):
            user = users[0]
            up = UserProfile.objects.get(user=user)

            state = row[header.index('STATE')]
            agency_name = row[header.index("UNIVERSITY")]
            pio = row[header.index("PIO OFFICER")]
            email = row[header.index("PIO Email")]
            phone = row[header.index("PIO Phone")]

            sid_pio = row[header.index("SID ")]
            sid_email = row[header.index("SID Email")]
            sid_phone = row[header.index("SID Phone")]

            is_power = (row[header.index("Power Conference")] == 'TRUE')
            is_private = (row[header.index("Is Private")] == 'TRUE')

            if not is_private and state != '' and email != 'N/A' and pio != 'N/A' and agency_name != '':
                govt = get_or_create_us_govt(state, 'state')
                fname = pio.split(" ")[0]
                lname = pio.split(" ")[-1]
                middle = ''
                #alter table `contacts_contact` convert to character set utf8 collate utf8_general_ci;
                #alter table `agency_agency` convert to character set utf8 collate utf8_general_ci;
                #alter table `requests_request` convert to character set utf8 collate utf8_general_ci;
                try:
                    agency, acreated = Agency.objects.get_or_create(name=agency_name, government=govt)
                except Exception as e:
                    print e
                    print "If more than one agency was returned, pick one!"
                    import pdb;pdb.set_trace() 
                try:
                    contact, ccreated = agency.contacts.get_or_create(first_name=fname, middle_name=middle, last_name=lname)
                except Exception as e:
                    print e
                    print "If more than one contact was returned, pick one!"
                    import pdb;pdb.set_trace()

                sid_contact = None

                if phone != 'N/A':
                    contact.add_phone(phone)
                contact.add_email(email)

                #agency.contacts.add(contact)

                if sid_pio != 'N/A' and sid_email != 'N/A':
                    fname = sid_pio.split(" ")[0]
                    lname = sid_pio.split(" ")[-1]
                    sid_contact, ccreated = Contact.objects.get_or_create(first_name=fname, middle_name='', last_name=lname)
                    sid_contact.add_title("SID")
                    sid_contact.add_email(sid_email)
                    if sid_phone != 'N/A':
                        sid_contact.add_phone(sid_phone)
                    agency.contacts.add(sid_contact)

                contacts = [contact]
                if sid_contact is not None:
                    contacts = [contact, sid_contact]

                agency.save()

                #logger.info('agency %s %s contact %s %s %s %s' % (agency_name, acreated, fname, middle, lname, ccreated))

                law_texts = []
                for l in govt.statutes.all():
                    law_texts.append('%s' % (l.short_title,))

                misc_graf = """
                    Please advise me in advance of the estimated charges associated with fulfilling \
                    this request.</br></br>In the interest of expediency, and to minimize the research\
                    and/or duplication burden on your staff, please send records electronically if possible.\
                    If this is not possible, please notify me by phone at %s before sending to the address listed below.
                """ % (up.phone)
                misc_graf += '<br/></br>Sincerly,<br/><br/>%s<br/>%s<br/>%s<br/>%s' % (user.first_name + ' ' + user.last_name, up.mailing_address, up.mailing_city + ', ' + up.mailing_state + ' ' + up.mailing_zip, up.phone)

                if not is_power:
                    fields_to_use = {
                        'author': user,
                        'title': 'NCAA Report - %s' % agency_name,
                        'free_edit_body': ncaa_text_to_use % (' and '.join(law_texts), misc_graf),
                        'private': True,
                        'text': ncaa_text_to_use
                    }
                    therequest = Request(**fields_to_use)
                    therequest.date_added = datetime.now()
                    therequest.save()
                    therequest.contacts = contacts
                    therequest.government = govt
                    therequest.agency = agency
                    therequest.tags.add(ncaa_tag_name)
                    therequest.save()

                    assign_perm(Request.get_permission_name('view'), ncaa_group, therequest)
                    #assign_perm(Request.get_permission_name('edit'), thegroup, therequest)

                coaches = [
                    'Football Coach',
                    'Offensive Coord.',
                    'Defensive Coord.',
                    "Men's BB Coach",
                    "Women's BB Coach"
                ]

                coaches_str = []
                for coach in coaches:
                    val = row[header.index(coach)].strip()
                    if val != 'N/A' and val != '':
                        coaches_str.append("%s (%s)" % (val, coach))
                        print val

                fields_to_use = {
                    'author': user,
                    'title': 'Coach Contracts - %s' % agency_name,
                    'free_edit_body': coach_text_to_use % (' and '.join(law_texts), ', '.join(coaches_str), misc_graf),
                    'private': True,
                    'text': coach_text_to_use
                }
                therequest = Request(**fields_to_use)
                therequest.date_added = datetime.now()
                therequest.save()
                therequest.contacts = contacts
                therequest.government = govt
                therequest.agency = agency
                therequest.tags.add(coach_tag_name)
                therequest.save()

                assign_perm(Request.get_permission_name('view'), coach_group, therequest)