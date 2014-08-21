from django.db import models
from django_extensions.db.fields import AutoSlugField
from apps.core.models import BaseData
from django.contrib.auth.models import User, Group
from django.utils.html import escape

import pytz
import datetime
import bleach
from django.utils import timezone

class Language(BaseData):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from=('name', ), overwrite=False)

    class Meta:
        verbose_name_plural = 'Languages'

    def __unicode__(self):
        return self.name
        
class AdminName(BaseData):
    name = models.CharField(max_length=255)
    name_plural = models.CharField(max_length=255, blank=True, null=True)

    def __unicode__(self):
        return self.name

class Update(BaseData):
    author = models.ForeignKey(User)
    pubbed = models.DateTimeField(null=True)
    headline = models.CharField(max_length=1024, default="The latest")
    text = models.TextField()

class FeeExemptionOtherManager(models.Manager):
    def all_them(self):
        return super(FeeExemptionOtherManager, self).get_query_set()

    def get_query_set(self):
        return super(FeeExemptionOtherManager, self).get_query_set().filter(deprecated__isnull=True)

class FeeExemptionOther(BaseData):
    statute_relation_types = (
        ('E', 'Exemption'),
        ('F', 'Fee'),
        ('O', 'Other'),
    )
    name = models.CharField(max_length=512)
    slug = AutoSlugField(populate_from=('name', ), overwrite=False)
    description = models.TextField(blank=True, null=True)
    source = models.URLField(blank=True, null=True)
    typee = models.CharField(max_length=1, choices=statute_relation_types,)
    objects = FeeExemptionOtherManager()

    def __unicode__(self):
        return self.name


    @property
    def deleted(self):
        return self.deprecated is not None

    @property
    def get_name(self):
        return bleach.clean(self.name, strip=True)

    @property
    def get_description(self):
        return bleach.clean(self.description, strip=True)

    @property
    def get_source(self):
        return bleach.clean(self.source, strip=True)

#Nation (for example, names for admin 1, 2, etc. levels, language modules)
class Nation(BaseData):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from=('name', ), overwrite=False)
    primary_language = models.ForeignKey(Language, related_name='primary_language_nations', blank=True, null=True)
    foi_languages = models.ManyToManyField(Language, blank=True, null=True)
    admin_0_name = models.ForeignKey(AdminName, null=True, blank=True, related_name='admin_0_nations')
    admin_1_name = models.ForeignKey(AdminName, null=True, blank=True, related_name='admin_1_nations')
    admin_2_name = models.ForeignKey(AdminName, null=True, blank=True, related_name='admin_2_nations')
    admin_3_name = models.ForeignKey(AdminName, null=True, blank=True, related_name='admin_3_nations')


    class Meta:
        verbose_name_plural = 'Nations'

    def __unicode__(self):
        return self.name


class StatuteManager(models.Manager):
    def all_them(self):
        return super(StatuteManager, self).get_query_set()

    def get_query_set(self):
        return super(StatuteManager, self).get_query_set().filter(deprecated__isnull=True)


class Statute(BaseData):
    short_title = models.CharField(max_length=255)
    designator = models.CharField(max_length=255, blank=True, null=True)
    text = models.TextField(blank=True,null=True)
    days_till_due = models.IntegerField(default=-1)
    slug = AutoSlugField(populate_from=('short_title', ), overwrite=False)
    fees_exemptions = models.ManyToManyField(FeeExemptionOther, null=True, blank=True)
    updates = models.ManyToManyField(Update, null=True, blank=True)
    #deleted = models.BooleanField(default = False)
    objects = StatuteManager()

    
    class Meta:
        verbose_name_plural = 'Statutes'

    def __unicode__(self):
        return self.short_title

    @property
    def deleted(self):
        return self.deprecated is not None

    @property
    def get_short_title(self):
        return bleach.clean(self.short_title, strip=True)

    @property
    def get_designator(self):
        return bleach.clean(self.designator, strip=True)

    @property
    def get_governments(self):
        return self.related_statutes.all()

    @property
    def get_text(self):
        return escape(self.text.trim())

    @property 
    def get_days_till_due(self):
        if self.days_till_due < 0:
            return None
        return self.days_till_due

class Holiday(BaseData):
    name = models.CharField(max_length = 255) # e.g. Christmas Day 2011, Casimir Pulaski Day 2013
    date = models.DateField()


class GovernmentManager(models.Manager):
    def get_query_set(self):
        return super(GovernmentManager, self).get_query_set().filter(deprecated__isnull=True)

class Government(BaseData):
    GOV_LEVELS = (
        ('I', 'International'),
        ('S', 'Supernational'),
        ('0', 'Admin 0 (National)'),
        ('1', 'Admin 1 (State/Province)'),
        ('2', 'Admin 2 (County or similar)'),
        ('3', 'Admin 3 (City or municipality)'),
    )
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from=('name', ), overwrite=False)
    level = models.CharField(max_length=1, choices=GOV_LEVELS)
    nation = models.ForeignKey(Nation, null=True, blank=True)
    statutes = models.ManyToManyField(Statute, null=True, blank=True, related_name='related_statutes')
    #deleted = models.BooleanField(default = False)
    holidays = models.ManyToManyField(Holiday, null=True, blank=True)
    objects = GovernmentManager()
    

    class Meta:
        verbose_name_plural = 'Governments'

    def __unicode__(self):
        return '%s (%s)' % (self.name, self.nation,)

    @property
    def get_holiday_dates(self):
        """ Default to U.S. federal holidays """
        utc = pytz.UTC
        holidays = self.holidays.all()
        if holidays:
            return [holiday.date for holiday in holidays]
        tz = timezone.get_current_timezone()
        datetuples = [
            (2013, 1, 1), # New Year's Day
            (2013, 1, 21),# Martin Luther King Jr. Day
            (2013, 2, 18),# Washington's Birthday
            (2013, 5, 27),# Memorial Day
            (2013, 7, 4), # Independence Day
            (2013, 9, 2), # Labor Day
            (2013, 10, 14), # Columbus Day
            (2013, 11, 11), # Veterans Day
            (2013, 11, 28), # Thanksgiving Day
            (2013, 12, 25), # Christmas Day
            (2014, 1, 1), # New Year's Day
            (2014, 1, 20), # Martin Luther King Jr. Day
            (2014, 2, 17), # Washington's Bday
            (2014, 5, 26), # Memorial Day
            (2014, 7, 4), # Independence Day
            (2014, 9, 1), # Labor Day
            (2014, 10, 13), # Columbus Day
            (2014, 11, 11), # Veterans' Day
            (2014, 11, 27), # Thanksgiving Day
            (2014, 12, 25) # Christmas Day
        ]
        return map(lambda datetuple: tz.localize(datetime.datetime(*datetuple)), datetuples)

    @property
    def get_statutes(self):
        if self.statutes.all().count() <= 0:
            return None
        return self.statutes.all().order_by('-days_till_due')

    @staticmethod
    def get_us_gov_levels():
        return {
            'state': 1,
            'county': 2,
            'city': 3
        }

