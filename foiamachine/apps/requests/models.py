from django.db import models
from django.dispatch import receiver
from django.core.urlresolvers import reverse
from django.core.files.base import ContentFile
from django.contrib.auth.models import User, Group
from django_extensions.db.fields import AutoSlugField
from django.db.models.signals import post_save
from django.db.models import Q
from django.utils import timezone

from apps.agency.models import Agency
from apps.contacts.models import Contact
from apps.core.models import EmailAddress
from apps.doccloud.models import Document
from apps.government.models import Government
#from apps.users.models import Group
from apps.mail.attachment import Attachment
from apps.requests.templatetags.filter_tags import excludeHiddenTags

from taggit.managers import TaggableManager
from guardian.shortcuts import assign, remove_perm,\
    get_objects_for_user, get_objects_for_group,\
    get_groups_with_perms

from datetime import datetime, timedelta
import workdays
import logging
import pytz

logger = logging.getLogger('default')

response_format_types = (
    ('FL', 'Flat'),
    ('GS', 'Geospatial'),
    ('DB', 'Database'),
)



class ResponseFormat(models.Model):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from=('name', ), overwrite=True)
    type = models.CharField(max_length=2, choices=response_format_types,)
    description = models.TextField(u'Description of this format', blank=True)
    file_extension = models.CharField(max_length=10, blank=True)

    class Meta:
        verbose_name_plural = 'Response formats'

    def __unicode__(self):
        return self.name


class RecordType(models.Model):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from=('name', ), overwrite=True)
    description = models.TextField(u'Description of this format', blank=True)

    class Meta:
        verbose_name_plural = 'Record types'

    def __unicode__(self):
        return self.name


request_statuses = (
    ('X', 'Deleted'),
    ('I', 'Incomplete'),
    ('U', 'New (Unsent)'),
    ('S', 'Filed (Request sent)'),
    ('R', 'Response received (but not complete)'),
    ('P', 'Partially fulfilled'),
    ('F', 'Fulfilled'),
    ('D', 'Denied'),
)



class PublicRequestManager(models.Manager):
    def for_agency(self, agency_slug):
        return self.get_query_set().filter(agency__slug=agency_slug)

    def for_group(self, group, level=None):
        group, created = Group.objects.get_or_create(name=group)
        if level is not None:
            return get_objects_for_group(group, Request.get_permissions_path(level))
        return get_objects_for_group(group, Request.get_permissions_path('view'))

    def for_government(self, govt_slug):
        return self.get_query_set().filter(government__slug=govt_slug)

    def get_query_set(self):
        group, created = Group.objects.get_or_create(name='public')
        return get_objects_for_group(group, Request.get_permissions_path('view')).filter(~Q(status='I'))


class PrivateRequestManager(models.Manager):
    def get_query_set(self):
        return super(PrivateRequestManager, self).get_query_set().filter(private=True)


class MyRequestManager(models.Manager):
    def for_group_a(self, group, level=None):
        group, created = Group.objects.get_or_create(name=group)
        if level is not None:
            return get_objects_for_group(group, Request.get_permissions_path(level)).filter(~Q(status='X'))
        return get_objects_for_group(group, Request.get_permissions_path('view')).filter(~Q(status='X'))

    def for_group(self, user, group, level=None):
        user_groups = [group.name for group in user.groups.all()]
        if group in user_groups:
            group, created = Group.objects.get_or_create(name=group)
            if level is not None:
                return get_objects_for_group(group, Request.get_permissions_path(level)).filter(~Q(status='X'))
            return get_objects_for_group(group, Request.get_permissions_path('view')).filter(~Q(status='X'))
        return []

    def for_user(self, user):
        return get_objects_for_user(user, Request.get_permissions_path('view')).filter(~Q(status='X'))

    def get_query_set(self):
        return super(MyRequestManager, self).get_query_set()


NOTIFICATION_TYPES = (
    (0, 'Late request'),
    (1, 'Remdiner to update request status'),
    (2, 'Sunset clause notification')
)

class Request(models.Model):
    author = models.ForeignKey(User)
    title = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=1, choices=request_statuses,)
    government = models.ForeignKey(Government, null=True, blank=True)
    agency = models.ForeignKey(Agency, blank=True, null=True)
    documents = models.ManyToManyField(Document, blank=True, null=True, related_name='related_docs')
    contacts = models.ManyToManyField(Contact, blank=True, null=True, related_name='related_contacts')
    text = models.TextField(u'Request text', blank=True)
    free_edit_body = models.TextField(u'Request text', blank=True)
    attachments = models.ManyToManyField(Attachment, blank=True, null=True)
    printed = models.ForeignKey(Attachment, blank=True, null=True, related_name='printed_request')
    private = models.BooleanField('Mark this request as private', default=True)
    supporters = models.ManyToManyField(User, blank=True, null=True, related_name='supporter')
    slug = AutoSlugField(populate_from=('title', ), overwrite=False, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    date_fulfilled = models.DateTimeField(blank=True, null=True)
    due_date = models.DateTimeField(blank = True, null = True)
    scheduled_send_date = models.DateTimeField(blank=True, null=True)
    request_start_date = models.DateTimeField(blank=True, null=True)
    request_end_date = models.DateTimeField(blank=True, null=True)
    keep_private = models.BooleanField('Never make this request public by default', default=False)
    #Different from response formats: things like "meeting minutes", e.g.
    record_types = models.ManyToManyField(RecordType, blank=True, null=True)
    acceptable_responses = models.ManyToManyField(ResponseFormat, blank=True, null=True)
    fee_waiver = models.BooleanField(default=True)
    phone_contact = models.BooleanField(default=True)
    prefer_electornic = models.BooleanField(default=True)
    max_cost = models.IntegerField(default=0, blank=True)
    thread_lookup = models.CharField(max_length=255, blank=True)


    last_contact_date = models.DateTimeField(blank=True, null=True)
    first_response_time = models.IntegerField(default=0, blank = True)
    lifetime = models.IntegerField(default = 0, blank = True)
    days_outstanding = models.IntegerField(default = 0, blank = True)
    response_overdue = models.BooleanField(default = False)
    official_stats = models.BooleanField(default = False)


    # Managers
    objects = MyRequestManager()

    private_objects = PrivateRequestManager()
    public_objects = PublicRequestManager()

    tags = TaggableManager(blank=True)

    @property
    def get_contacts_with_email(self):
        retval = []
        for contact in self.contacts.all():
            if contact.get_first_active_email is None:
                retval.append(contact)
        return retval

    def set_status(self, status_str):
        old_status = self.status
        for rs in request_statuses:
            if status_str == rs[1] or status_str == rs[0]:
                self.status = rs[0]
                new_status = self.status

                if old_status == 'S' and (new_status in ['R','P','F','D']) and self.scheduled_send_date is not None:
                    # Our first response from the agency
                    now = datetime.now(tz=pytz.utc)
                    holidays = self.government.get_holiday_dates
                    self.first_response_time = workdays.networkdays(self.scheduled_send_date, now, holidays)
                    if self.first_response_time == 0:
                        self.first_response_time = 1


                if old_status in ['S', 'R', 'P'] and new_status in ['F', 'D'] and self.scheduled_send_date is not None:
                    now = datetime.now(tz=pytz.utc)
                    holidays = self.government.get_holiday_dates
                    self.lifetime = workdays.networkdays(self.scheduled_send_date, now, holidays)
                    if self.lifetime == 0:
                        self.lifetime = 1
                self.save()
        return self.get_status

    @property
    def get_status(self):
        for rs in request_statuses:
            if self.status == rs[0]:
                return rs[1]
        return self.status

    @property
    def get_privacy_string(self):
        shared_with = get_groups_with_perms(self)
        retval = "Nothing"
        if self.private == True and len(shared_with) == 1:
            retval = "This request is private"
        elif self.private == True and len(shared_with) > 1:#TODO DOUBLE CHECK ME
            retval = "This request is private but shared with others"
        else:
            retval = "This request is public"
        return retval

    @property
    def get_title_string(self):
        if self.title == '':
            return 'Unspecified'
        return self.title

    @property
    def get_status_color(self):
        try:
            mapp = {
                'X': '#d73027',
                'I': '#f46d43',
                'U': '#fdae61',
                'S': '#fee090',
                'R': '#e0f3f8',
                'P': '#abd9e9',
                'F': '#74add1',
                'D': '#4575b4'
            }
            return mapp[self.status]
        except:
            return ""

    @property
    def get_due_date_string(self):
        if self.due_date:
            return self.due_date.strftime("%b %d, %Y")
        return 'NA'

    @property
    def get_date_added_string(self):
        if self.date_added:
            try:
                return self.date_added.strftime("%b %d, %Y")
            except Exception as e:
                logger.error(e)
        return 'NA'

    @property
    def get_date_updated_string(self):
        if self.date_added:
            try:
                return self.date_updated.strftime("%b %d, %Y")
            except Exception as e:
                logger.error(e)
        return 'NA'

    @property
    def get_agency_string(self):
        if self.agency:
            url = reverse('agency_detail', args=(self.agency.slug,))
            return "<a href='%s'>%s</a>" % (url, self.agency.name)
        return "NA"

    @property
    def get_government_string(self):
        if self.government:
            retval = ""
            for statute in self.government.statutes.all():
                url = reverse("statute_detail", args=(statute.slug,))
                retval += "<a href='%s'>%s</a>" % (url, statute.short_title)
            return retval
        return "NA"

    @property
    def get_tags_string(self):
        retval = ""
        tags = excludeHiddenTags(self.tags.all())
        if len(tags) <= 0:
            return "None"
        for idx, tag in enumerate(tags):
            retval += "<a href='?tags=%s&filtering=1'>%s</a>" % (tag.id, tag.name)
            if idx != len(tags) - 1:
                retval += ', '
        return retval

    @property
    def get_detail_url(self):
        return reverse("request_detail", args=(self.id,))

    @property
    def can_send(self):
        if self.sent:
            return False
        if self.contacts.all().count() < 1:
            return False
        if self.agency is None:
            return False
        if self.government is None:
            return False
        if self.free_edit_body == '':
            return False
        return True

    @property
    def sent(self):
        #this is the for sure way but scheduled_send_date is set when the object is mailed and we currently have no scheduler
        from apps.mail.models import MailBox
        mb = MailBox.objects.get_or_create(usr=self.author)[0]
        threads = mb.get_threads(self.id)
        #TODO update this so it checks the sent date, because now people can send emails to an unsent request
        if len(threads) > 0:
            return True
        return False

    @property
    def get_due_date(self):
        #get statute with least number of days till maturity
        #TODO: scheduled send date should probably be required and checked against the first sent message
        if self.due_date:
            return self.due_date
        if self.government is None:
            return None
        statutes = self.government.get_statutes
        holidays = self.government.get_holiday_dates
        if statutes is not None and self.scheduled_send_date is not None:
            if len(statutes) > 0:
                soonest_statute = statutes[0]
            else:
                return None
            days_till_due = soonest_statute.get_days_till_due
            if days_till_due:
                sent = self.scheduled_send_date
                due_when = workdays.workday(sent, days_till_due, holidays)
                self.due_date = due_when
            else:
                self.due_date = None
            self.save()
            return self.due_date
        return None

    @property
    def get_days_till_due(self):
        due_date = self.get_due_date
        if due_date is not None:
            dt = due_date - self.scheduled_send_date
            return dt.days
        return None

    class Meta:
        permissions = (
            ('view_this_request', 'View request'),
            ('edit_this_request', 'Edit request'),
            ('delete_this_request', 'Delete request'),
        )

    @staticmethod
    def get_permission_name(key):
    #provide map for standard permissions
        permissions_map = {
            'view': 'view_this_request',
            'edit': 'edit_this_request',
            'delete': 'delete_this_request'
        }
        try:
            return permissions_map[key]
        except KeyError:
            return ''

    @staticmethod
    def get_permissions_path(key):
        return 'requests.%s' % Request.get_permission_name(key)

    def __unicode__(self):
        if self.agency:
            return '%s: %s %s %s' % (self.agency, self.date_added, self.title, self.id)
        elif self.government:
            return '%s (No agency yet): %s %s %s' % (self.government, self.date_added, self.title, self.id)
        else:
            return '%s %s' % (str(self.date_added), self.id)

    @property
    def letter_header(self):
        address = ''
        for c in self.contacts.all():
            address += '<div class="well"><address><div class="contact-name">%s %s</div>' % (c.first_name, c.last_name,)
            title = c.get_recent_title()
            if title:
                 address += '<div class="contact-address">%s</div>' % (title.get_content,)
            snail_mail = c.get_recent_address()
            if snail_mail:
                address += '<div class="contact-address">%s</div>' % (snail_mail.get_content,)
            emails = c.get_active_emails()
            if emails:
                emails = [email.get_email for email in emails]
                address += '<div class="contact-email">%s</div></address>' % (','.join(emails))
            address += '<p>Dear %s:</p></div>' % (c.first_name,)
        return address

    @property
    def letter_body(self):
        try:
            body = ''
            #law citation handling
            law_texts = []
            statutes = self.government.statutes.all() if self.government is not None else []
            for l in statutes:
                law_texts.append('%s\'s %s (%s)' % (self.government.name, l.short_title, l.designator,))
            #short_title, designator
            body += '<p>Pursuant to %s, I hereby request the following records:</p>' % (' and '.join(law_texts))
            #items requested
            body += '<p>%s</p>' % (self.text,)
            #formats
            if self.acceptable_responses.all().count() == 1:
                body += '<p>I would like to request that my request be fulfilled in the form of a %s.</p>'\
                 % (self.acceptable_responses.all()[0],)
            elif self.acceptable_responses.all().count() > 0:
                formats = '<p>I would like my request be fulfilled in one of these electronic formats:</p><ul>'
                for f in self.acceptable_responses.all():
                    formats += '<li>%s</li>' % (f,)
                formats += '</ul>'
                body += formats
            #fee warning
            cost_graf = ''
            if len(statutes) > 0:
                cost_graf = 'Under the %s the government is allowed to charge only the cost of\
                 copying materials.' % (statutes[0].short_title,)
            #TODO: fee waiver
            if self.fee_waiver:
                cost_graf += ' I am requesting that you waive all applicable fees associated with this request as I believe this request is in the public interest and is not for commercial use. Release of this information is in the public interest because it will contribute significantly to public understanding of government operations and activities. If you deny this request for a fee waiver, please advise me in advance of the estimated charges'
                if self.max_cost == 0:
                    cost_graf += ' associated with fulfilling this request.'
                else:
                    cost_graf += ' if they are to exceed $%s.' % (self.max_cost,)
            else:
                #no fee waiver
                if self.max_cost == 0:
                    cost_graf += ' Please advise me in advance of the estimated charges associated with fulfilling this request.'
                else:
                    cost_graf += ' Please advise me in advance of the estimated charges if they are to exceed $%s.' % (self.max_cost,)

            cost_graf += ' Please send me a detailed and itemized explanation of those charges.'
            body += '<p>%s</p>' % (cost_graf,)
            misc_graf = ''
            if self.prefer_electornic:
                misc_graf += 'In the interest of expediency, and to minimize the research and/or duplication burden on your staff, please send records electronically if possible.  If this is not possible, please notify me before sending to the address listed below.'
            if self.phone_contact:
                from apps.users.models import UserProfile
                phone = UserProfile.objects.get(user=self.author).phone
                misc_graf += ' Since time is a factor, please communicate with me by telephone or this email address. I can be reached at %s' % phone

            body += '<p>%s</p>' % (misc_graf,)

            #contact graf
            body += '<p>Please contact me if you have any questions about my request.</p>'
        except Exception as e:
            logger.exception(e)
        return body

    @property
    def letter_signature(self):
        from apps.users.models import UserProfile
        authorprofile = UserProfile.objects.get(user=self.author)
        #TODO set users phone number
        retval = '<p>%s %s</p>' % (self.author.first_name, self.author.last_name,)
        retval += '<p>%s<br/>%s<br/>%s<br/>%s, %s %s</p>'\
             % (self.author.email, authorprofile.phone, authorprofile.mailing_address,  authorprofile.mailing_city, authorprofile.mailing_state, authorprofile.mailing_zip,)
        return retval

    @property
    def letter_html(self):
        letter = '%s%s<p>Sincerely,</p>%s' % (self.letter_header, self.letter_body, self.letter_signature,)
        return letter

    def create_pdf_body(self):
        from apps.mail.models import Attachment
        from xhtml2pdf import pisa
        import os
        try:
            #ghetto tmp file for pdf creation, will this work on HEROKU? I think so but could be slow...
            if not os.path.exists('tmp'):
                os.makedirs('tmp')
            #TODO: need default attachment
            attachment = None
            html = self.free_edit_body
            fname = 'tmp/request_%s_tmp.pdf' % self.id
            with open(fname, 'wb') as f:
                doc = pisa.pisaDocument(html, f)
            if not doc.err:
                with open(fname, 'rb') as f:
                    to_file = ContentFile(f.read())
                    attachment = Attachment()
                    attachment.user = self.author
                    attachment.file.save('request_%s.pdf' % self.id, to_file)
                    attachment.save()
                os.remove(fname)
            else:
                logger.error("error writing to PDF: %s" % doc.err)
            self.printed = attachment
            self.save()
            return attachment.url
        except Exception as e:
            logger.exception(e)
            return None 

    def send(self, attachments=[]):
        if self.sent:
            return True
        try:
            #avoid circular imports
            from apps.mail.models import MailBox, MailMessage, MSG_DIRECTIONS
            mailbox, created = MailBox.objects.get_or_create(usr=self.author)
            #attachment = self.create_pdf_body()
            tos = []
            for contact in self.contacts.all():
                tos += [email for email in contact.get_active_emails()]
            bcc_email, created = EmailAddress.objects.get_or_create(content=self.author.email)
            subject = self.title if self.title is not None and self.title != '' else 'Open Records Request for %s %s' % (contact.first_name, contact.last_name,)
            message = MailMessage(email_from=mailbox.get_registered_email(),
                subject=subject,\
                body=self.free_edit_body.encode('utf8'), reply_to=mailbox.get_provisioned_email(),\
                direction=MSG_DIRECTIONS[0][0], request=self)
            message.save()

            message.to = tos
            message.bcc = [bcc_email]
            #message.attachments = [attachment] if attachment is not None else []
            message.attachments = []
            if attachments:
                for attach in attachments:
                    message.attachments.add(attach)
            for attach in self.attachments.all():
                message.attachments.add(attach)
            sent = message.send(mailbox.get_provisioned_email())
            mailbox.add_message(message)
            #update status
            self.status = 'S'
            self.scheduled_send_date = timezone.now()
            self.due_date = self.get_due_date
            self.save()
            if sent is None:
                return False
            return True
        except Exception as e:
            logger.exception(e)
            return False 

    @property
    def privacy_status(self):
        if self.private:
            return 'Private'
        else:
            return 'Public'

    @property
    def time_outstanding(self):
        date_filed = self.date_added
        if self.date_fulfilled:
            final_date = self.date_fulfilled
        else:
            final_date = timezone.now()
        date_diff = final_date - date_filed
        return date_diff.days

    def original_deadline(self):
        try: # AHHHH HACK CITY!!!
            e = self.event_set.filter(type=2).order_by('date')[0]
        except IndexError:
            return
        return e.date

    @property
    def latest_deadline(self):
        try: # AHHHH HACK CITY!!!
            e = self.event_set.filter(type=2).order_by('date')[0]
        except IndexError:
            return
        return e.date

    @property
    def is_late_naive(self):
        """
        Naive representation of whether a response is late. Will
        want to redo this with more 
        """
        is_late = False
        if self.latest_deadline: # AHHHH HACK CITY!!!
            if datetime.date.today() > self.latest_deadline:
                is_late = True
        return is_late


    @models.permalink
    def get_absolute_url(self):
        return ('request_detail', (), {'pk': self.pk})

    def save(self, *args, **kw):
        #TODO: abort save if sent
        if self.pk is not None:
            orig = Request.objects.get(pk=self.pk)
            if orig.private != self.private:
                logger.info("request %s privacy changed to=%s from=%s" % (self.slug, self.private, orig.private))
                group, g_created = Group.objects.get_or_create(name='public')
                if self.private == True:
                    remove_perm(Request.get_permission_name('view'), group, self)
                    logger.info('request %s permissions changed: removed from public' % (self.slug))
                else:
                    assign(Request.get_permission_name('view'), group, self)
                    logger.info('request %s permissions changed: added to public' % (self.slug))
            #import pdb;pdb.set_trace()
            if self.contacts is not None and self.contacts.count() > 0 and self.contacts.all()[0].get_related_agencies().count() > 0:
                self.agency = self.contacts.all()[0].get_related_agencies()[0]
                self.government = self.agency.government
            else:
                self.agency = None
                self.government = None
        else:
            self.status = 'I'
            code = "LOOKUP:" + User.objects.make_random_password(length=64)
            while Request.objects.filter(thread_lookup=code):
                code = User.objects.make_random_password(length=64)
            self.thread_lookup = code
        super(Request, self).save(*args, **kw)

    @staticmethod
    def get_user_in_threshold(user, days=7):
        now = datetime.now(tz=pytz.utc)
        threshold = now - timedelta(days=days)
        return Request.objects.filter(author=user, date_added__gte=threshold, status__in=['S','R','P','F','D'])

    @staticmethod
    def get_all_overdue(days=1):
        now = datetime.now(tz=pytz.utc).strftime("%Y-%m-%d") + " 23:59:59"
        query = (
            "select requests_request.id from requests_request"
            " where requests_request.due_date <= '%s' and requests_request.due_date"
            " is not null and requests_request.status = 'S' and"
            " requests_request.id not in (select request_id from requests_notification where type = %s);" % (now, Notification.get_type_id('Late request'))
            )
        results = Request.objects.raw(query, translations={'requsts_request.id': 'id'})
        return set(results)

    @staticmethod
    def get_all_sunsetting(sunset_days):
        now = (datetime.now(tz=pytz.utc) + timedelta(-1 * (sunset_days-1))).strftime("%Y-%m-%d")
        query = (
            "select requests_request.id from requests_request"
            " where requests_request.scheduled_send_date <= '%s' and requests_request.scheduled_send_date"
            " is not null and requests_request.private = 1 and requests_request.keep_private = 0 and"
            " requests_request.status != 'X' and requests_request.status != 'I' and requests_request.status != 'U' and"
            " requests_request.id not in (select request_id from requests_notification where type = %s);" % (now, Notification.get_type_id('Sunset clause notification'))
            )
        results = Request.objects.raw(query, translations={'requsts_request.id': 'id'})
        return set(results)

    @staticmethod
    def get_sunsetted(sunset_days):
        now = (datetime.now(tz=pytz.utc) + timedelta(-1 * (sunset_days-1))).strftime("%Y-%m-%d") + " 23:59:59"
        #only want to make requests public for users who have received a notification of sunset
        #BUT the raw query defers model loading which breaks django_guardian
        #query = (
        #    "select requests_request.id from requests_request"
        #    " where requests_request.scheduled_send_date <= '%s' and requests_request.scheduled_send_date"
        #    " is not null and requests_request.status = 'S' and requests_request.private = 1 and requests_request.keep_private = 0 and"
        #    " requests_request.id in (select request_id from requests_notification where type = %s);" % (now, Notification.get_type_id('Sunset clause notification'))
        #    )
        #results = Request.objects.raw(query, translations={'requsts_request.id': 'id'})
        #return set(results)
        return Request.objects.filter(private=True, scheduled_send_date__lte=now, keep_private=False)

class ViewableLink(models.Model):
    owner = models.ForeignKey(User, null=True)
    request = models.ForeignKey(Request, blank = True, null = True)
    tags = TaggableManager(blank=True)
    code = models.CharField(max_length = 255, blank = True)

class Notification(models.Model):
    type = models.IntegerField(choices=NOTIFICATION_TYPES)
    sent = models.DateField(auto_now_add=True, blank=True, null=True)
    request = models.ForeignKey(Request, null=True, blank=True)

    def __unicode__(self):
        return '%s:%s' % (self.type, self.get_type_name)

    @property
    def get_type_name(self):
        for t in NOTIFICATION_TYPES:
            if type == t[0]:
                return t[1]

    @staticmethod
    def get_type_id(type_str):
        for t in NOTIFICATION_TYPES:
            if type_str == t[1]:
                return t[0]

    @staticmethod
    def get_type_name(type_id):
        for t in NOTIFICATION_TYPES:
            if type_id == t[0]:
                return t[1]


#Use for request target
class Organization(models.Model):
    name = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = models.DateField(blank=True, null=True)
    postal_code = models.CharField(max_length=255, blank=True)

    def __unicode__(self):
        return self.name


class Event(models.Model):
    EVENT_CHOICES = (
        (0, 'Note'),
        (1, 'Reminder'),
        (2, 'Deadline'),
        (3, 'Response')
    )
    request = models.ForeignKey(Request)
    type = models.IntegerField(choices=EVENT_CHOICES)
    name = models.CharField(max_length=255)
    date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)
    # Supporting docs

    def __unicode__(self):
        return '%s -> %s' % (self.request.title, self.name)



@receiver(post_save, sender=Request)
def set_request_permissions(sender, **kwargs):
    obj = kwargs['instance']
    created = kwargs['created']
    #import pdb;pdb.set_trace()
    if created:
        try:
            my_group, g_created = Group.objects.get_or_create(name=obj.author.username)
            assign(Request.get_permission_name('view'), my_group, obj)
            assign(Request.get_permission_name('edit'), my_group, obj)
            assign(Request.get_permission_name('delete'), my_group, obj)
            logger.info('user has perm: %s' % obj.author.has_perm('view_this_request', obj))
            logger.info('group for user %s created=%s, permissions set for request %s' % (obj.author.username, g_created, obj.id))
            if not obj.private:
                group, g_created = Group.objects.get_or_create(name='public')
                assign(Request.get_permission_name('view'), group, obj)
                logger.info('request %s added to public, public_created=%s' % (obj.slug, g_created))
        except Exception as e:
            logger.exception(e)
    logger.info('request %s updated' % obj.id)
