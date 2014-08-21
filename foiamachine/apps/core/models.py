from django.db import models
from datetime import datetime
from django.utils import timezone

from taggit.managers import TaggableManager

class BaseData(models.Model):
    '''
    base model to allow depreciation of existing 
    fields and store votes to let users tell the system
    how accurate we are if prompted

    TODO we may want to use this approach on more models than those in contacts
    '''
    created = models.DateTimeField(auto_now_add=True)
    deprecated = models.DateTimeField(null=True)
    yay_votes = models.PositiveSmallIntegerField(default=0)
    nay_votes = models.PositiveSmallIntegerField(default=0)
    tags = TaggableManager()

    def deactive(self):
        self.deprecated = timezone.now()
        self.save()

    class Meta:
        abstract = True

    @property
    def get_content(self):
        pass

class EmailsManager(models.Manager):

    def all_them(self):
        return super(EmailsManager, self).get_query_set().all()

    def get_query_set(self):
        return super(EmailsManager, self).get_query_set().filter(deprecated__isnull=True)



class EmailAddress(BaseData):
    #unique so duplicate emails aren't stored in this table
    #always use get_or_create
    content = models.EmailField()
    objects = EmailsManager()


    def __unicode__(self):
        return self.content

    @staticmethod
    def get_or_create(email):
        #a fake interface, better practice for when handling changes to fields
        te, created = EmailAddress.objects.get_or_create(content=email)
        return (te, created)

    @property
    def get_email(self):
        return self.content

    def set_email(self, email):
        self.content = email
        
