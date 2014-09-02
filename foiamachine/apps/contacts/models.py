from django.contrib.auth.models import User
from django.db.models import Q
from django.db import models
from django.db.models import Count


from apps.core.models import BaseData, EmailAddress

import logging

logger = logging.getLogger('default')

class Title(BaseData):
    content = models.CharField(max_length=255, blank=True)
    
    @property
    def get_content(self):
        return self.content

    def __unicode__(self):
        return self.content

class Phone(BaseData):
    '''
    not using localflavors bc it's deprecated
    TODO dwell on how to handle this
    thought was I could use charfield of 15 digis
    but no consistent extension formatting appears in our data 
    and some cells have multiple numbers comma delimited
    but extensions are also comma delimited

    if we are printing out the number for someone else to call
    we just need to print out the string and ask them if it was
    right, that's probably better than enforcing 
    '''
    content = models.CharField(max_length=512)

    @property
    def get_content(self):
        return self.content

    def __unicode__(self):
        return self.content

class Address(BaseData):
    '''
    could be international so lets store the address as a blob
    '''
    content = models.TextField()

    @property
    def get_content(self):
        return self.content

    def __unicode__(self):
        return self.content

class Note(BaseData):
    '''
    let a user leave a note on an contact
    '''
    content = models.TextField()
    user = models.ForeignKey(User, null=True)

    @property
    def get_content(self):
        return self.content
        
    def __unicode__(self):
        return self.content


class ContactsManager(models.Manager):

    def all_them(self):
        return super(ContactsManager, self).get_query_set().annotate(Count('emails')).all()

    def get_query_set(self):
        return super(ContactsManager, self).get_query_set().annotate(Count('emails')).filter(deprecated__isnull=True, hidden=False)


class Contact(BaseData):
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    middle_name = models.CharField(max_length=255, blank=True)
    dob = models.DateField(blank=True, null=True)
    notes = models.ManyToManyField(Note, blank=True, null=True)
    titles = models.ManyToManyField(Title, blank=True, null=True)
    emails = models.ManyToManyField(EmailAddress, blank=True, null=True)
    phone_numbers = models.ManyToManyField(Phone, blank=True, null=True)
    addresses = models.ManyToManyField(Address, blank=True, null=True)
    creator = models.ForeignKey(User, null=True)
    hidden = models.BooleanField(default=False)
    objects = ContactsManager()

    def __unicode__(self):
        return '%s %s' % (self.first_name, self.last_name)

    def get_related_agencies(self):
        return self.agency_related_contacts.all()

    def set_new_agency(self, new_agency):
        for agency in self.get_related_agencies():
            agency.contacts.remove(self)
        new_agency.contacts.add(self)
        new_agency.save()

    def add_phone(self, number):
        tp = Phone(content=number)
        tp.save()
        if self.phone_numbers.all().count() <= 0:
            self.phone_numbers = [tp]
        else:
            self.phone_numbers.add(tp)

    def add_email(self, email):
        te, created = EmailAddress.get_or_create(email)
        if self.emails.filter(pk=te.pk).count() == 0:
            self.emails.add(te)
        te.save()

    def add_title(self, title):
        tt = Title(content=title)
        tt.save()
        if self.titles.all().count() <= 0:
            self.titles = [tt]
        else:
            self.titles.add(tt)

    def add_address(self, address):
        ta = Address(content=address)
        ta.save()
        if self.addresses.all().count() <= 0:
            self.addresses = [ta]
        else:
            self.addresses.add(ta)

    def add_note(self, note, user=None):
        tn = Note(content=note, user=user)
        tn.save()
        if self.notes.all().count() <= 0:
            self.notes = [tn]
        else:
            self.notes.add(tn)

    def get_active_phones(self):
        return self.phone_numbers.filter(deprecated=None)

    @property
    def get_first_active_email(self):
        if self.get_active_emails().count() > 0:
            return self.emails.filter(deprecated=None).all()[0]
        return None

    @property
    def get_first_active_address(self):
        if self.get_active_addressess().count() > 0:
            return self.addresses.filter(deprecated=None).all()[0]
        return None

    @property
    def get_first_active_phone(self):
        if self.get_active_phones().count() > 0:
            return self.phone_numbers.filter(deprecated=None).all()[0]
        return None

    @property
    def get_active_emails_t(self):
        return self.emails.filter(deprecated=None)

    def get_active_emails(self):
        return self.emails.filter(deprecated=None)

    def get_active_titles(self):
        return self.titles.filter(deprecated=None)

    def get_active_addressess(self):
        return self.addresses.filter(deprecated=None)

    def get_recent_title(self):
        try:
            return self.titles.filter(deprecated=None).order_by('-created')[0]
        except Exception as e:
            logger.info(e)
            return ''

    def get_recent_address(self):
        try:
            return self.addresses.filter(deprecated=None).order_by('-created')[0]
        except Exception as e:
            logger.info(e)
            return '' 
