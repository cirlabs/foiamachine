from django.contrib.auth.models import User
from django.db import models
from django_extensions.db.fields import AutoSlugField
from apps.government.models import Government
from apps.core.models import BaseData
from apps.contacts.models import Contact
from datetime import datetime
from django.utils import timezone


class AgencyManager(models.Manager):
    def all_them(self):
        return super(AgencyManager, self).get_query_set().filter(deprecated__isnull=True).prefetch_related("government", "creator")

    def get_query_set(self):
        return super(AgencyManager, self).get_query_set().filter(deprecated__isnull=True, hidden=False).prefetch_related("government", "creator")

class Agency(BaseData):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from=('name', ), overwrite=False)
    government = models.ForeignKey(Government)
    contacts = models.ManyToManyField(Contact, blank=True, null=True, related_name='agency_related_contacts')
    objects = AgencyManager()
    creator = models.ForeignKey(User, null = True)
    hidden = models.BooleanField(default =  False)
    pub_contact_cnt = models.IntegerField(default=0)
    editor_contact_cnt = models.IntegerField(default=0)


    class Meta:
        verbose_name_plural = 'Agencies'

    def __unicode__(self):
        return self.name

    def has_editable_contact(self, usr):
        for contact in self.contacts.all():
            if contact.creator == usr:
                return True
        return False

    @property
    def late_requests(self):
        """
        How many requests have FAILED to meet their deadlines?
        """
        num_late_requests = 0
        for r in self.related_agencies.all():
            if r.is_late_naive: num_late_requests += 1
        return num_late_requests

    @property
    def average_time_outstanding(self):
        days_late = 0
        for r in self.related_agencies.all():
            days_late += r.time_outstanding
        return days_late 

    def save(self, *args, **kw):
        if self.pk is not None:
            self.pub_contact_cnt = self.contacts.filter(hidden=False).count()
            self.editor_contact_cnt = self.contacts.all().count()
        else:
            self.pub_contact_cnt = 0
            self.editor_contact_cnt = 0
        super(Agency, self).save(*args, **kw)
