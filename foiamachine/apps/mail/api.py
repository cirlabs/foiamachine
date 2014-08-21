#!/usr/bin/python
from apps.mail.models import MailBox, MailMessage, Attachment
from apps.core.models import EmailAddress
from apps.requests.models import Request

from tastypie import fields
from tastypie.resources import ModelResource, Resource
from tastypie.authorization import Authorization, DjangoAuthorization

from django.utils import timezone
from datetime import datetime
from apps.users.models import User


import logging

logger = logging.getLogger('default')


class MessageResource(ModelResource):
    
    class Meta:
        resource_name = 'message'
        allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'put']
        authorization = Authorization()
        queryset = MailMessage.objects.all()
        always_return_data = True 

    def dehydrate(self, bundle):
        for attr in ['id', 'email_from', 'reply_to', 'body', 'subject', 'request','id', 'message_id', 'direction', 'created', 'updated', 'slug', 'deprecated']:
            bundle.data[attr] = getattr(bundle.obj, attr)
        if bundle.data['request']:
            bundle.data['request'] = bundle.data['request'].id

        bundle.data['replies'] = map(lambda x: x.id, bundle.obj.replies.all())
        bundle.data['attachments'] = map(lambda x: [x.file.url, x.get_filename], bundle.obj.attachments.all())
        bundle.data['dated'] = bundle.data['dated'].strftime("%B %d, %Y %I:%M %p")
        bundle.data['was_fwded'] = bundle.obj.was_fwded
        for attr in ['bcc', 'cc', 'to']:
            bundle.data[attr] = map(str, getattr(bundle.obj, attr).all())
        #import pdb;pdb.set_trace()
        return bundle

    def obj_update(self, bundle, **kwargs):
        user = bundle.request.user
        if 'request' not in bundle.data:
            raise BadRequest("No request to associate with")
        data = bundle.data
        request = Request.objects.get(id=data['request'])
        if not user.has_perm(Request.get_permission_name('edit'), request):
            return bundle
        try:
            data = bundle.data
            message = bundle.obj = MailMessage.objects.get(id=data['id'])
            for field in ['body', 'subject', 'deprecated']:
                if field in data:
                    setattr(message, field, data[field])
            message.save()
            return bundle
        except Exception as e:
            logger.exception(e)
            raise BadRequest(str(e))
        return bundle

    def obj_create(self, bundle, **kwargs):
        try:
            data = bundle.data
            user = bundle.request.user
            mb = MailBox.objects.get(usr=user)
            parent = None
            if 'following' in bundle.data:
                parent = MailMessage.objects.get(id=bundle.data['following'])
                del bundle.data['following']

            bcc = []
            cc = []
            to = []
            attachments = []
            request = None
            if 'request' in data:
                request = Request.objects.get(id=data['request'])
                del data['request']

            if request is None:
                return bundle

            if not user.has_perm(Request.get_permission_name('edit'), request):
                return bundle

            if 'bcc' in data:
                bcc = data['bcc']
                del data['bcc']

            if 'cc' in data:
                cc = data['cc']
                del data['cc']

            if 'to' in data:
                to = data['to']
                del data['to']

            if 'attachments' in data:
                attachments = [Attachment.objects.get(id=id) for id in data['attachments']]
                del data['attachments']


            theMessage = MailMessage(**data)
            theMessage.save()
            for address in to:
                item, created = EmailAddress.objects.get_or_create(content=address)
                item.save()
                theMessage.to.add(item)
            for address in bcc:
                item, created = EmailAddress.objects.get_or_create(content=address)
                item.save()
                theMessage.bcc.add(item)
            for address in cc:
                item, created = EmailAddress.objects.get_or_create(content=address)
                item.save()
                theMessage.cc.add(item)
            if request:
                theMessage.request = request

            for attachment in attachments:
                theMessage.attachments.add(attachment)
            

            if parent:
                parent.replies.add(theMessage)
                parent.save()

            theMessage.dated = timezone.now()
            theMessage.save()
            mb.messages.add(theMessage)
            mb.save()
            bundle.obj = theMessage
        except Exception as e:
            logger.exception(e)
        return bundle

    def get_object_list(self, request):
        try:
            return MailBox.objects.get(usr=request.user).messages
        except Exception as e:
            logger.info(e)
            return []


