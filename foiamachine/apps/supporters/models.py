from django.db import models
import locale

import logging

logger = logging.getLogger('default')


class SupportLevel(models.Model):
    name = models.CharField(max_length=255, blank=True)
    minimum_amount = models.IntegerField()
    active = models.BooleanField(default=True)

    def __unicode__(self):
        locale.setlocale(locale.LC_ALL, '')
        return '%s ($%s or more)' % (self.name, locale.format("%d", self.minimum_amount, grouping=True),)

    @property
    def sorted_supporter_set(self):
        return self.supporter_set.order_by('name')


class SupporterManager(models.Manager):
    def get_queryset(self):
        return super(SupporterManager, self).get_queryset().filter(active=True)


class Supporter(models.Model):
    kickstarter_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=255, blank=True)
    support_level = models.ForeignKey(SupportLevel, null=True, blank=True)
    active = models.BooleanField(default=True)

    objects = SupporterManager()

    def __unicode__(self):
        return self.name
