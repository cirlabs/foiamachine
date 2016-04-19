from django.db import models
from django.db.models import Q
from django.conf import settings
from django_extensions.db.fields import AutoSlugField
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import timezone

from werkzeug.datastructures import MultiDict

from time import mktime
import simplejson as json
from datetime import datetime
from StringIO import StringIO
from email.utils import parseaddr, parsedate
from dateutil.parser import parse
from attachment import *

from apps.requests.models import Request
from apps.core.models import EmailAddress

import django
import mimetypes
import requests
import poplib
import email
import logging
import boto
import re

logger = logging.getLogger('default')
thread_pattern = re.compile("LOOKUP:[a-zA-Z1234567890]*")

MSG_DIRECTIONS = (
    ('S', 'SENT'),
    ('R', "RECEIVED")
)

class MessageId(models.Model):
    #messageid should never be more than 250, we do 512 just in case
    #http://www.imc.org/ietf-usefor/2000/Jun/0020.html
    idd = models.CharField(max_length=255, unique=True)

    @property
    def get_msg_id(self):
        return self.idd

class MailManager(models.Manager):
    def get_query_set(self):
        return super(MailManager, self).get_query_set().filter(deprecated__isnull=True)

class MailMessage(models.Model):
    email_from = models.EmailField(max_length=256)
    reply_to = models.EmailField(blank=True, null=True)
    to = models.ManyToManyField(EmailAddress, blank=True, null=True, related_name='message_to')
    cc = models.ManyToManyField(EmailAddress, blank=True, null=True, related_name='message_cc')
    bcc = models.ManyToManyField(EmailAddress, blank=True, null=True, related_name='message_bcc')
    body = models.TextField(blank=True, null=True)
    subject = models.CharField(max_length=1024)
    attachments = models.ManyToManyField(Attachment, blank=True, null=True, related_name='message_attachments')
    request = models.ForeignKey(Request, blank=True, null=True)
    replies = models.ManyToManyField("self", null=True, blank=True, related_name='prior_thread')
    #if it is a reply, then time it was received by mail server otherwise NOW
    dated = models.DateTimeField(null=True, blank=True)
    #when message was created on our database, if sent by us then created == dated
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    slug = AutoSlugField(populate_from=('subject',), overwrite=False)
    direction = models.CharField(max_length=1, choices=MSG_DIRECTIONS,)
    message_id = models.CharField(max_length=255, blank=True, null=True)
    #todo move to using the MessageId class
    received_header = models.TextField(null=True, blank=True)
    references = models.ManyToManyField(MessageId, blank=True, null=True, related_name='message_references')
    deprecated = models.DateTimeField(null=True)
    was_fwded = models.BooleanField('this message was sent by a user to this thread', default=False)

    objects = MailManager()

    @staticmethod
    def get_notes():
        #message id is set by mailgun / mail server so unsent messages or user notes have no id
        return MailMessage.objects.filter(message_id__isnull=True)

    def get_mailboxes(self):
        return self.mailbox_messages.all()

    def get_email_addresses(self):
        retval = []
        retval = retval + [address.get_email for address in self.to.all()]
        retval = retval + [address.get_email for address in self.cc.all()]
        retval = retval + [address.get_email for address in self.bcc.all()]
        retval = retval + [self.email_from]
        retval = retval + [self.reply_to]
        retval = [address for address in retval if address] # Remove any 'Nones'
        return retval

    @property
    def get_references_hdr(self):
        retval = [reference.get_msg_id for reference in self.references.all()]
        return "\t".join(retval)

    @property
    def get_reference_ids(self):
        return [reference.get_msg_id for reference in self.references.all()]

    def add_references(self, references):
        for reference in references:
            self.references.add(reference)

    @property
    def get_from_email(self):
        return self.email_from

    @property
    def get_to_emails(self):
        return [to.content for to in self.to.all()]

    @property
    def get_cc_emails(self):
        return [cc.content for cc in self.cc.all()]

    @property
    def plain_text_body(self):
        from HTMLParser import HTMLParser

        class MLStripper(HTMLParser):
            def __init__(self):
                self.reset()
                self.fed = []

            def handle_data(self, d):
                self.fed.append(d)

            def get_data(self):
                return ''.join(self.fed)

        s = MLStripper()
        s.feed(self.body)
        return s.get_data()

    @property
    def get_body(self):
        return self.body.replace("\r", "<br/>")

    def send(self, provisioned_address, references=None):
        data = {"from": self.email_from,
            "to": [addr.get_email for addr in self.to.all()] + ([provisioned_address] if hasattr(settings, 'MG_ROUTE') else []),
            "subject": self.subject,
            #"h:reply-to": self.reply_to,
            "html": self.body
        }
        if references is not None:
            data['h:References'] = references
        if self.bcc.all().count() > 0:
            data['bcc'] = [addr.get_email for addr in self.bcc.all()]
        if self.cc.all().count() > 0:
            data['cc'] = [addr.get_email for addr in self.cc.all()]

        resp = requests.post(
                settings.MG_POST_URL,
                files=MultiDict([("attachment", attachment.file) for attachment in self.attachments.all()]),
                auth=("api", settings.MAILGUN_KEY),
                data=data)
        content = json.loads(resp.content)
        self.dated = timezone.now()
        logging.info('MESSAGE SEND STATUS:%s' % resp.content)
        retval = None
        if "id" in content.keys():
            logger.info("SENT MESSAGE message_id=%s" % content['id'])
            self.message_id = content['id']
            retval = content['id']
        self.save()
        return retval


class MailBox(models.Model):
    usr = models.ForeignKey(django.contrib.auth.models.User)
    messages = models.ManyToManyField(MailMessage, blank=True, null=True, related_name='mailbox_messages')
    created = models.DateTimeField(auto_now_add=True)
    provisioned_email = models.EmailField(blank=True, null=True)

    def get_orphaned_messages(self):
        return self.messages.filter(request__id=None).order_by('-dated')

    @staticmethod
    def get_root(request_id):
        return MailMessage.objects.filter(request__id=request_id).order_by('dated')[0]

    def get_threads(self, request_id):
        #roots = self.messages.filter(request__id=request_id).order_by('dated')
        roots = MailMessage.objects.filter(request__id=request_id).order_by('dated')
        logger.debug("getting threads len=%s request_id=%s" % (roots.count(), request_id))
        if roots.count() <= 0:
            return list()
        if roots.count() > 0:
            return [roots[0]] + [mail_msg for mail_msg in roots[0].replies.all().order_by('dated')]
        if roots[0].dated is not None and roots[0].dated >= datetime(month=3, day=18, year=2013):
            retval = [reply for reply in roots[0].replies.all()]
            retval.insert(0, roots[0])
            return retval
        return []

    def add_message(self, message):
        self.messages.add(message)

    def check_and_save_mail(self):
        messages = self.check_mail()
        for message in messages:
            try:
                mail_msg, inreply = self.parse_message_poptres(message)
                self.store_message(mail_msg, inreply)
            except Exception as e:
                logger.exception(e)
        return True

    def check_mail(self):
        '''
        TODO I need to delete messages that have been stored
        which should be taken care of with a wrapper method
        that deletes messages after I have stored them
        '''
        M = poplib.POP3(settings.MAILGUN_POP)
        M.user(self.get_provisioned_email())
        M.pass_(self.get_password())

        numMessages = len(M.list()[1])
        retval = list()
        for i in range(numMessages):
            msg = M.retr(i+1)[1]
            mail = email.message_from_string('\n'.join(msg))
            retval.append(mail)
        return retval

    def parse_message_poptres(self, message):
        '''
        http://www.ietf.org/rfc/rfc2822.txt
        '''
        body = None
        html = None
        subject = message['Subject']

        from_email = parseaddr(message.get('From'))[1]
        tos = [EmailAddress.objects.get_or_create(content=parseaddr(msg)[1])[0]
               for msg in message.get_all('to', [])]
        ccs = [EmailAddress.objects.get_or_create(content=parseaddr(msg)[1])[0]
               for msg in message.get_all('cc', [])]
        dt = parsedate(message.get('Date'))
        datet = datetime.fromtimestamp(mktime(dt)) if dt is not None else dt
        inreply = message.get('In-Reply-To', None)

        message_id = message.get('Message-Id', None)
        raw_header = ""
        for key in message.keys():
            raw_header += '\n' + message.get(key)
        attachments = list()

        for part in message.walk():
            content_disposition = part.get("Content-Disposition", None)
            if content_disposition:
                atch = self.parse_attachments_poptres(content_disposition, part)
                attachments.append(atch)
            elif part.get_content_type() == "text/plain":
                if body is None:
                    body = ""
                body += unicode(
                    part.get_payload(decode=True),
                    part.get_content_charset(),
                    'replace'
                ).encode('utf8', 'replace')
            elif part.get_content_type() == "text/html":
                if html is None:
                    html = ""
                html += unicode(
                    part.get_payload(decode=True),
                    part.get_content_charset(),
                    'replace'
                ).encode('utf8', 'replace')

        body = html if html is not None else body

        #don't save messages we already have
        if MailMessage.objects.filter(message_id=message_id).count() > 0:
            logger.debug('duplicate message found message_id=%s' % message_id)
            return None
        if MailMessage.objects.filter(body=body).count() > 0:
            ids = [obj.message_id for obj in MailMessage.objects.filter(body=body)]
            logger.debug('duplicate body found, ignoring message_id=%s' % ids)
            return None

        references = message.get('References', None)
        references = [MessageId.objects.get_or_create(idd=reference)[0]
                      for reference in references.split("\t")] if references is not None else []

        logger.debug('message_id=%s' % message_id)
        mail_msg = MailMessage(subject=subject, email_from=from_email,
                               direction=MSG_DIRECTIONS[1][0], dated=datet, message_id=message_id,
                               received_header=raw_header)

        mail_msg.body = body
        mail_msg.save()
        mail_msg.references = references
        mail_msg.attachments = attachments
        mail_msg.to = tos
        mail_msg.cc = ccs
        mail_msg.dated = datet
        self.messages.add(mail_msg)
        return (mail_msg, inreply)

    @staticmethod
    def parse_message_http(keyvals):
        try:
            from_email = keyvals['sender'] if 'sender' in keyvals.keys() else ''
            message_id = keyvals['Message-Id'] if 'Message-Id' in keyvals.keys() else ''
            references = keyvals['References'] if 'References' in keyvals.keys() else ''
            inreply = keyvals['In-Reply-To'] if 'In-Reply-To' in keyvals.keys() else ''
            text_body = keyvals['body-plain'] if 'body-plain' in keyvals.keys() else ''
            html_body = keyvals['body-html'] if 'body-html' in keyvals.keys() else ''
            body = text_body if not html_body else html_body
            subject = keyvals['subject'] if 'subject' in keyvals.keys() else ''
            dt = keyvals['Date'] if 'Date' in keyvals.keys() else None
            datet = parse(dt) if dt is not None else dt
            raw_header = ''

            logger.info('message parsed id=%s' % message_id)

            tosi = keyvals['To'].split(',') if 'To' in keyvals.keys() else []
            ccsi = keyvals['Cc'].split(',') if 'Cc' in keyvals.keys() else []

            from_email = parseaddr(from_email)[1]
            tos = [EmailAddress.objects.get_or_create(content=parseaddr(msg)[1])[0]
                   for msg in tosi]
            ccs = [EmailAddress.objects.get_or_create(content=parseaddr(msg)[1])[0]
                   for msg in ccsi]


            logger.info('PREREFERENCES=%s' % references)
            references = [MessageId.objects.get_or_create(idd=reference)[0]
                          for reference in references.split()] if references is not None else []

            logger.info('REFERENCES=%s' % references)

            mail_msg = MailMessage(subject=subject, email_from=from_email,
                                   direction=MSG_DIRECTIONS[1][0], dated=datet, message_id=message_id,
                                   received_header=raw_header)

            mail_msg.body = body
            mail_msg.save()
            logger.info('message saved pk=%s' % mail_msg.id)
            mail_msg.references = references
            mail_msg.to = tos
            mail_msg.cc = ccs
            #self.messages.add(mail_msg)
            return (mail_msg, inreply)

        except Exception as e:
            logger.exception("error parsing message e=%s" % (e))

        return (None)

    def store_message(self, mail_msg, inreply, files):
        #mail_msg, inreply = self.parse_message_poptres(message)
        attachments = []
        try:
            for key in files:
                f = files[key]
                logger.info('FILE=%s' % f)
                atch = Attachment()
                atch.user = self.usr
                atch.file.save(f.name, f)
                atch.save()
                attachments.append(atch)
        except Exception as e:
            logger.exception('cant parse attachment e=%s' % e)

        mail_msg.attachments = attachments
        if inreply:
            try:
                logger.info('this message=%s looking up message in reply to: %s' % (mail_msg.message_id, inreply))
                refs = mail_msg.get_reference_ids
                logger.info('REFERENCES = %s' % refs)
                '''
                Email RFC details the references header
                http://tools.ietf.org/html/rfc2822#section-3.6.4
                it is how we create a thread in this app
                find all messages referred to in the references header
                find the oldest one and add THIS message to its replies
                '''
                threads = self.messages.filter(message_id__in=refs).order_by('dated')
                rthreads = filter(lambda x: x.request is not None, threads)
                thread = rthreads[0] if len(rthreads) > 0 else threads[0] if threads.count() > 0 else None
                if thread is None:
                    self.lookup_thread(mail_msg)
                else:
                    if thread.request is not None:
                        thread = MailMessage.objects.filter(request__id=thread.request.id).order_by('dated')[0] 
                    thread.replies.add(mail_msg)
                    #mail_msg.request = thread.request
                    mail_msg.save()
                    #make sure all messages know about each other
                    mail_msg.add_references(thread.references.all())
                    thread.add_references(mail_msg.references.all())
                    logger.info('FOUND thread message_id=%s' % thread.message_id)
                    logger.info('THREADS request %s' % thread.request)
                    logger.info('THREADS replies %s' % [mm.message_id for mm in thread.replies.all()])
                    mail_msg.reply_to = self.get_provisioned_email()
                    mail_msg.was_fwded = True#update the fact the message was forwarded
                    #self.lookup_thread(mail_msg)

                    cnt = thread.replies.all().filter(message_id__isnull=False).count()
                    #if this is the first reply
                    #if cnt == 1:
                    #    status = thread.request.set_status("Response received (but not complete)")

            except Exception as e:
                logger.exception('tried to lookup root message and send but failed e=%s' % e)
                self.lookup_thread(mail_msg)
        else:
            self.lookup_thread(mail_msg)
        return mail_msg

    def lookup_thread(self, mail_msg):
        any_matches = [thread_pattern.findall(mail_msg.body), thread_pattern.findall(mail_msg.subject)]
        for any_match in any_matches:
            for match in any_match:
                logger.debug("FOUND MATCH =%s" % match)
                for req in Request.objects.filter(thread_lookup=match):
                    threads = self.get_threads(req.id)
                    logger.debug("LOOKUP CODE THREAD COUNT =%s" % len(threads))
                    if len(threads) > 0:#messages have been sent!
                        thread = threads[0]
                        thread.replies.add(mail_msg)
                        mail_msg.add_references(thread.references.all())
                        mail_msg.was_fwded = True
                        thread.add_references(mail_msg.references.all())
                    else:#message was never sent
                        mail_msg.request = req
                    mail_msg.save() 
        return mail_msg

    def parse_attachments_poptres(self, content_disposition, part):
        dispositions = content_disposition.strip().split(";")
        if bool(content_disposition and dispositions[0].lower() == "attachment"):

            file_data = part.get_payload(decode=True)
            attachment = StringIO(file_data)
            attachment.content_type = part.get_content_type()
            attachment.size = len(file_data)
            attachment.name = None
            attachment.create_date = None
            attachment.mod_date = None
            attachment.read_date = None

            for param in dispositions[1:]:
                name, value = param.split("=")
                name = name.lower().strip()
                value = value.replace('"', '').strip()

                if name == "filename":
                    attachment.name = value
                elif name == "create-date":
                    attachment.create_date = value
                elif name == "modification-date":
                    attachment.mod_date = value
                elif name == "read-date":
                    attachment.read_date = value

            attachment.seek(0, 2)
            f = InMemoryUploadedFile(attachment, "", attachment.name, attachment.content_type, attachment.tell(), None)

            atch = Attachment()
            atch.user = self.usr
            atch.file.save(attachment.name, f)
            atch.save()
            return atch

    def get_provisioned_email(self):
        if hasattr(settings, 'MG_ROUTE'):
            # Fix this beore commit
            thisaddress = "%s@%s.%s" % (self.usr.username.split("@")[0], settings.MG_ROUTE, settings.MG_DOMAIN)
        else:
            thisaddress = "%s@%s" % (self.usr.username.split("@")[0], settings.MG_DOMAIN)
        logger.info("THIS address=%s" % thisaddress)
        if self.provisioned_email is None or self.provisioned_email != thisaddress:
            self.provisioned_email = thisaddress
            self.save()
        return self.provisioned_email

    def get_registered_email(self):
        return self.usr.email
