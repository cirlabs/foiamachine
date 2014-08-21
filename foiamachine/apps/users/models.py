from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group
from django_extensions.db.fields import AutoSlugField

from django.conf import settings
from guardian.shortcuts import get_perms, get_users_with_perms, get_objects_for_user, assign_perm
from taggit.managers import TaggableManager


from apps.requests.models import Request

import logging

logger = logging.getLogger('default')


class ActivationKeyValue(models.Model):
    """
    Key Value pair to lookup a user after we have sent out their
    activation email
    """
    created = models.DateTimeField(auto_now_add=True)
    key = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.key


class InterestedParty(models.Model):
    INTEREST_CHOICES = (
        ('F', 'Following a request'),
        ('S', 'Sending and sharing FOI requests'),
        ('C', 'Contributing contacts and best practices'),
        ('O', 'Other'),
    )
    first_name = models.CharField(max_length=512)
    last_name = models.CharField(max_length=512)
    email = models.EmailField(unique=True)
    created = models.DateTimeField(auto_now_add=True)
    activated_on = models.DateTimeField(blank=True, null=True)
    activation_key = models.ForeignKey(ActivationKeyValue, blank=True, null=True)
    interested_in = models.CharField(max_length=3, choices=INTEREST_CHOICES)
    followed_request = models.ManyToManyField(Request, blank=True, null=True,)

    class Meta:
        verbose_name_plural = 'interested parties'

    def __unicode__(self):
        return self.name

    @property
    def name(self):
        return '%s %s' % (self.first_name, self.last_name)

    @property
    def get_interested(self):
        result = filter(lambda k: k[0] == self.interested_in, self.INTEREST_CHOICES)
        return result[0][1]


class Project(models.Model):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from=('name', ), overwrite=False)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.name

class Organization(models.Model):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from=('name', ), overwrite=False)
    logo = models.ImageField(upload_to='logos', blank=True, null=True, max_length=255)

    def __unicode__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    mailing_address = models.CharField(max_length=150, blank=True)
    mailing_city = models.CharField(max_length=50, blank=True)
    mailing_state = models.CharField(max_length=20, blank=True)
    mailing_zip = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    private_by_default = models.BooleanField(default=False)
    organizations = models.ManyToManyField(Organization, blank=True, null=True)
    is_pro = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    timezone = models.CharField(max_length=150, default='UTC')
    requests_per_week = models.IntegerField(default = 30)
    tags = TaggableManager(blank=True)
    default_request_creator_free = models.BooleanField(default=False)


    def __unicode__(self):
        return self.get_username()

    @staticmethod
    def get_permission_name(key):
        #provide map for standard permissions
        #override django guardian to use django's default permission settings for changing a group in the auth_permission
        #this indicates the user is the owner of the group
        #WHY this was done
        #at this point in development I can't subclass Group and to add additional permissions
        #I need a Meta class or to manually insert a new row into auth_permission which would break syncdb
        #(in the senese the addtional step is a barrier to setting up a fresh instance easily)
        permissions_map = {
            'edit': 'change_group',
            'view': 'add_group'
        }
        try:
            return permissions_map[key]
        except KeyError:
            return ''

    def get_username(self):
        return self.user.username

    def get_email(self):
        return self.user.email

    def get_permissions(self, request_id):
        return get_perms(self.user, Request.objects.get(id=request_id))

    def get_viewable_objects(self):
        return get_objects_for_user(self.user)

    def save(self, *args, **kw):
        #TODO: abort save if sent
        if self.pk is not None:
            orig = UserProfile.objects.get(pk=self.pk)
            if self.user.email != orig.user.email:
                self.is_verified = false
                logger.info('user %s changed email %s to %s' % (self.user.username, self.user.email, orig.user.email))
        super(UserProfile, self).save(*args, **kw)


class PermissionGroup(models.Model):
#     PERM_TYPE_CHOICES = (
#         ('u', 'User'),
#         ('o', 'Organization'),
#         ('p', 'Public'),
#     )
    PERM_TYPE_CHOICES = (
        ('r', 'Read'),
        ('e', 'Edit'),
        ('d', 'Delete'),
    )
    type = models.CharField(max_length=3, choices=PERM_TYPE_CHOICES)
    requests = models.ManyToManyField(Request)
    users = models.ManyToManyField(User, blank=True, null=True,)
    organizations = models.ManyToManyField(Organization, blank=True, null=True,)

    def __unicode__(self):
        return self.type

@receiver(post_save, sender=User)
def add_user_to_public_group(sender, **kwargs):
    obj = kwargs['instance']
    created = kwargs['created']
    if created:
        try:
            up = UserProfile.objects.get(user=obj)
        except Exception as e:
            logger.info("NO userprofile for user %s" % obj.username)
            if not obj.username == 'AnonymousUser':
                up = UserProfile(user=obj)
                up.save()
        group, created = Group.objects.get_or_create(name='public')
        obj.groups.add(group)
        my_group, created = Group.objects.get_or_create(name=obj.username) 
        obj.groups.add(my_group)
        assign_perm(UserProfile.get_permission_name('edit'), obj, my_group)
        logger.info('user %s added to public' % obj.username)
    logger.info('user %s updated' % obj.username)

@receiver(post_save, sender=InterestedParty)
def send_thanks_for_registering(sender, **kwargs):
    obj = kwargs['instance']
    created = kwargs['created']
    if created and not settings.DEBUG:
        try: 
            from apps.users.utils import send_thanks
            send_thanks([obj])
        except Exception as e:
            logger.exception(e)
    logger.info('interested party %s updated' % obj.id)

def get_non_user_groups():
    return [group for group in Group.objects.all() if group.user_set.count() != 1 or group.user_set.all()[0].username != group.name]
