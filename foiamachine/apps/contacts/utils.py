from apps.government.utils import get_defaults, get_or_create_us_govt
from apps.agency.models import Agency
from apps.contacts.models import Contact
from django.conf import settings
import logging
import xlrd
import requests
import os

logger = logging.getLogger('default')

def create_mdrange_contacts():
    language, ntn, govt = get_defaults()
    govt = get_or_create_us_govt('California', 'state')
    agency, created = Agency.objects.get_or_create(name="California Department of Public Health", government=govt)
    contact, created = Contact.objects.get_or_create(first_name='default', middle_name='', last_name='contact')
    contact.save()
    contact.add_email('cdph.internetadmin@cdph.ca.gov')
    agency.contacts.add(contact)
    contact, created = Contact.objects.get_or_create(first_name='Ken', middle_name='', last_name='August')
    contact.save()
    contact.add_email('ken.august@cdph.ca.gov')
    agency.contacts.add(contact)



def create_msmith_contacts():
    language, ntn, govt = get_defaults()
    govt = get_or_create_us_govt('The City and County of San Francisco', 'city')
    agency, created = Agency.objects.get_or_create(name="Mayor's Office on Economic and Work Development", government=govt)
    contact, created = Contact.objects.get_or_create(first_name='Myisha', middle_name='', last_name='Hervey')
    contact.save()
    contact.add_email('myisha.hervey@sfgov.org')
    contact.add_phone('415.554.6969')
    agency.contacts.add(contact)

    agency, created = Agency.objects.get_or_create(name="Office of Community Investment and Infrastructure", government=govt)
    contact, created = Contact.objects.get_or_create(first_name='Natasha', middle_name='', last_name='Jones')
    contact.save()
    contact.add_email('natasha.jones@sfgov.org')
    contact.add_phone('415.749.2458')
    contact.add_phone('fax:415.749.2525')
    agency.contacts.add(contact)

    agency, created = Agency.objects.get_or_create(name="CEQA and Central Records Public Records Requests", government=govt)
    contact, created = Contact.objects.get_or_create(first_name='Stanley', middle_name='', last_name='Muraoka')
    contact.save()
    contact.add_email('Stanley.Muraoka@sfgov.org')
    contact.add_phone('415-749-2577')
    agency.contacts.add(contact)

    agency, created = Agency.objects.get_or_create(name="CEQA and Central Records Public Records Requests", government=govt)
    contact, created = Contact.objects.get_or_create(first_name='Stanley', middle_name='', last_name='Muraoka')
    contact.save()
    contact.add_email('Stanley.Muraoka@sfgov.org')
    contact.add_phone('415-749-2577')
    agency.contacts.add(contact)

    agency, created = Agency.objects.get_or_create(name="Mayor's Sunshine/FOIA Office", government=govt)
    contact, created = Contact.objects.get_or_create(first_name='NA', middle_name='', last_name='NA')
    contact.save()
    contact.add_email('MayorSunshineRequests@sfgov.org')
    agency.contacts.add(contact)


def create_test_contacts():
    language, ntn, govt = get_defaults()

    agency, created = Agency.objects.get_or_create(name='THE TEST AGENCY', government=govt)
    
    contact, created = Contact.objects.get_or_create(first_name='shane', middle_name='allen',
        last_name='shifflett')
    if created:
        contact.add_email('shifflett.shane@gmail.com')
    agency.contacts.add(contact)

    contact, created = Contact.objects.get_or_create(first_name='Another', middle_name='allen',
        last_name='Shane')
    if created:
        contact.add_email('sshifflett@cironline.org')
    agency.contacts.add(contact)

    contact, created = Contact.objects.get_or_create(first_name='coulter', middle_name='x',
        last_name='jones')
    if created:
        contact.add_email('coulterjones@gmail.com')
    agency.contacts.add(contact)


    contact, created = Contact.objects.get_or_create(first_name='mike', middle_name='x',
        last_name='corey')
    if created:
        contact.add_email('mikejcorey@gmail.com')
    agency.contacts.add(contact)


    contact, created = Contact.objects.get_or_create(first_name='Djordje', middle_name='x',
        last_name='Padejski')
    if created:
        contact.add_email('djordje.padejski@gmail.com')
    agency.contacts.add(contact)


    contact, created = Contact.objects.get_or_create(first_name='David', middle_name='x',
        last_name='Suriano')
    if created:
        contact.add_email('dave.suriano@gmail.com')
    agency.contacts.add(contact)

    contact, created = Contact.objects.get_or_create(first_name='Steven', middle_name='x',
        last_name='Melendez')
    if created:
        contact.add_email('smelendez@gmail.com')
    agency.contacts.add(contact)


def update_federal_contacts(local=True):
    '''
    if not local:
        obj = requests.get('http://www.foia.gov/full-foia-contacts.xls')
        wb = xlrd.open_workbook(file_contents=obj.content)
    '''
    wb = xlrd.open_workbook(filename=os.path.join(settings.SITE_ROOT, 'apps/contacts/data/updated-federal.xls'))
    sheet_names = [u'Agencies', 'Departments']
    #lvl, created = GovernmentLevel.objects.get_or_create(name="Admin 0 (National)", hierarchy_level=4)
    language, ntn, govt = get_defaults()

    for sn in sheet_names:
        sh = wb.sheet_by_name(sn)
        num_rows = sh.nrows - 1
        print 'numrows=%s' % num_rows
        row = 0#header
        while row < num_rows:
            row += 1
            create_contact(sh, row, govt)
        print 'row=%s sheet=%s' % (row, sn)

def update_california_contacts(local=True):
    wb = xlrd.open_workbook(filename=os.path.join(settings.SITE_ROOT, 'apps/contacts/data/ca-state-contacts.xlsx'))
    sheet_names = [u'FOIA Contacts',]
    language, ntn, govt = get_defaults()
    govt = get_or_create_us_govt('California', 'state')

    for sn in sheet_names:
        sh = wb.sheet_by_name(sn)
        num_rows = sh.nrows - 1
        row = 0#header
        while row < num_rows:
            row += 1
            create_ca_contact(sh, row, govt)

def create_contact(sh, row, govt):
    '''
    put agency name and note together as its name
    '''
    try:
        agency_name = sh.cell(row, 0).value.strip()
        #note = sh.cell(row, 1).value.strip()
        #agency_name = agency_name + '/' + note
        name = sh.cell(row, 1).value.strip().split(' ')
        fname, middle, lname = ('', '', '')
        if len(name) == 1:
            fname = name[0]
        elif len(name) == 2:
            fname = name[0]
            lname = name[1]
        elif len(name) > 2:
            fname = name[0]
            middle = name[1]
            lname = name[2]
        title = sh.cell(row, 2).value.strip()
    except Exception as e:
        print e
        import pdb;pdb.set_trace()
    
    email = sh.cell(row, 10).value.strip().split('mailto:')

    agency, created = Agency.objects.get_or_create(name=agency_name, government=govt)
    #i wish each contact had an agency field because this is a good way to associate the wrong contact with an agency
    #contact, created = Contact.objects.get_or_create(first_name=fname, middle_name=middle,
    #    last_name=lname)
    contact = Contact(first_name=fname, middle_name=middle, last_name=lname)
    logger.info('created %s %s %s' % (fname, middle, lname))
    contact.save()
    agency.contacts.add(contact)
    #contact.add_note(note)
    contact.add_title(title)
    #contact.add_address(address)
    #contact.add_phone(phone)
    if len(email) > 1:
        mail = email[1]
    else:
        mail = email[0]
    contact.add_email(mail)
    try:
        tags = str(sh.cell(row, 13).value).split(',')
        for tag in tags:
            tag = tag.strip()
            if tag != '':
                print 'tag added %s' % tag
                agency.tags.add(tag)
    except Exception as e:
        print '%s' % (e)


def create_ca_contact(sh, row, govt):
    '''
    put agency name and note together as its name
    '''
    agency_name = sh.cell(row, 0).value.strip()
    note = sh.cell(row, 1).value.strip()
    agency_name = agency_name + '/' + note
    name = sh.cell(row, 2).value.strip().split(' ')
    fname, middle, lname = ('', '', '')
    if len(name) == 1:
        fname = name[0]
    elif len(name) == 2:
        fname = name[0]
        lname = name[1]
    elif len(name) > 2:
        fname = name[0]
        middle = name[1]
        lname = name[2]
    title = sh.cell(row, 3).value.strip()
    adr_idx = [5, 6, 7, 8]
    address = str(sh.cell(row, 4).value).strip()
    for idx in adr_idx:
        address += ' ' + str(sh.cell(row, idx).value).strip()
    phone = sh.cell(row, 9).value.strip()
    email = sh.cell(row, 11).value.strip().split('mailto:')
    '''
    note += '\n website: ' + sh.cell(row, 12).value.strip()
    note += '\n online form:' + sh.cell(row, 13).value.strip()
    '''

    #only add contacts with emails for now
    if len(email) > 1:
        agency, created = Agency.objects.get_or_create(name=agency_name, government=govt)
        contact, created = Contact.objects.get_or_create(first_name=fname, middle_name=middle,
            last_name=lname)
        logger.info('created %s %s %s' % (fname, middle, lname))
        contact.save()
        agency.contacts.add(contact)
        contact.add_note(note)
        contact.add_title(title)
        contact.add_address(address)
        contact.add_phone(phone)
        contact.add_email(email[1])
        try:
            tags = str(sh.cell(row, 16).value).split(',')
            for tag in tags:
                tag = tag.strip()
                if tag != '':
                    print 'tag added %s' % tag
                    agency.tags.add(tag)
        except Exception as e:
            print '%s' % (e)