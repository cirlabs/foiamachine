from django.db.models import Count, Avg
from datetime import datetime
from apps.requests.models import Request, ViewableLink
from apps.agency.models import Agency
from apps.contacts.models import Contact
from apps.users.models import Group
from apps.users.api import GroupResource
from apps.agency.api import AgencyResource
from apps.contacts.api import ContactResource
from apps.users.models import User
from apps.users.api import TagResource, GroupResource
from guardian.models import GroupObjectPermission
from guardian.shortcuts import get_objects_for_group
from apps.mail.attachment import Attachment

from tastypie import fields
from tastypie.resources import ModelResource, Resource
from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS

from tastypie.authorization import Authorization, DjangoAuthorization
from tastypie.validation import Validation
from taggit.models import Tag

from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpBadRequest, HttpForbidden

from apps.users.models import UserProfile

from django.db.models import Q

import logging

logger = logging.getLogger('default')


def associate_contacts(bundle, data):
    try:
        retval = list()
        for dt in data['contacts']:
            contact = Contact.objects.get(id=dt['id'])
            retval.append(contact)
        del data['contacts']
        return retval 
    except Exception as e:
        logger.error(e)
    return []
        

class ViewableLinkResource(ModelResource):
    class Meta:
        authorization = Authorization()
        allowed_methods = ['get', 'put', 'post']
        detail_allowed_methods = ['get', 'put', 'post']
        queryset = ViewableLink.objects

    def get_object_list(self, request):
        return self.Meta.queryset.filter(owner=request.user)

    def obj_create(self, bundle, **kwargs):
        try: 
            data = bundle.data
            if not 'tags' in data and not 'request' in data:
                # Failed -- nothing to link to
                return bundle
            code = User.objects.make_random_password(length=64)
            while ViewableLink.objects.filter(code=code):
                code = User.objects.make_random_password(length=64)
            
            theobj = ViewableLink(code=code)
            theobj.save()
            theobj.owner = bundle.request.user
            if 'tags' in data:
                tags = data['tags']
                theobj.tags.add(*tags)

            if 'request' in data:
                theobj.request = Request.objects.get(id=data['request'])

            theobj.save()
            bundle.obj = theobj
        except Exception as e:
            logger.exception(e)
        return bundle


class StatsResource(ModelResource):

    class Meta:
        allowed_methods = ['get']
        detail_allowed_methods = ['get']
        authorization = Authorization()
        limit =3

    def get_object_list(self, request):
        return self.Meta.queryset.annotate(num_requests=Count('request')).order_by('-num_requests')
        

    def dehydrate(self, bundle):
        bundle.data = {}
        request_set = bundle.obj.request_set.exclude(agency__name='THE TEST AGENCY')
        if 'start_date' in bundle.request.GET:
            try:
                start_date = bundle.request.GET['start_date']
                dt = datetime.strptime(start_date, "%Y-%m-%d")
                request_set = request_set.exclude(date_updated__lt=dt)
            except:
                # Couldn't parse date
                pass
        if 'end_date' in bundle.request.GET:
            try:
                end_date = bundle.request.GET['end_date']
                dt = datetime.strptime(end_date, "%Y-%m-%d")
                request_set = request_set.exclude(date_updated__gt=dt)
            except:
                # Couldn't parse date
                pass
        bundle.data['num_sent'] = request_set.filter(scheduled_send_date__lte=datetime.now()).count()
        bundle.data['total_agencies'] = Agency.objects.all().count()
        bundle.data['sent_to_feds'] = request_set.filter(scheduled_send_date__lte=datetime.now(), government__name='United States of America').count()
        bundle.data['num_agencies'] = len(set(request_set.filter(agency__isnull=False, scheduled_send_date__lte=datetime.now()).values_list("agency", flat=True)))
        bundle.data['num_governments'] = len(set(request_set.filter(government__isnull=False, scheduled_send_date__lte=datetime.now()).values_list("government", flat=True)))
        bundle.data['num_requests_filed'] = request_set.exclude(status='X').exclude(status='I').exclude(status='U').count()
        bundle.data['num_partially_fulfilled'] = request_set.filter(status='P').count()
        bundle.data['num_fulfilled'] = request_set.filter(status='F').count()
        bundle.data['num_denied'] = request_set.filter(status='D').count()
        bundle.data['num_other_responses'] = request_set.filter(status='R').count()
        bundle.data['num_no_response'] = request_set.filter(status='S').count()
        bundle.data['num_response_overdue'] = request_set.filter(response_overdue=True).count()
        bundle.data['avg_first_response_time'] = request_set.filter(first_response_time__gt=0).aggregate(Avg('first_response_time'))['first_response_time__avg']
        bundle.data['avg_lifetime'] = request_set.filter(lifetime__gt=0).aggregate(Avg('lifetime'))['lifetime__avg']
        bundle.data['avg_days_outstanding'] = request_set.filter(days_outstanding__gt=0).aggregate(Avg('days_outstanding'))['days_outstanding__avg']
        bundle.data['id'] = bundle.obj.id
        return bundle

class AgencyStatsResource(StatsResource):

    class Meta(StatsResource.Meta):
        queryset = Agency.objects.filter(request__status__in=['P','F','D','R','S'])
        resource_name = 'agencystats'

    def dehydrate(self, bundle):
        bundle = super(AgencyStatsResource, self).dehydrate(bundle)
        bundle.data['name'] = bundle.obj.name
        return bundle



class UserStatsResource(StatsResource):

    class Meta(StatsResource.Meta):
        queryset = User.objects.filter(request__status__in=['P','F','D','R','S'])
        resource_name = 'userstats'

    def get_object_list(self, request):
        user = request.user
        result = super(UserStatsResource, self).get_object_list(request)

        if user.is_superuser:
            return result

        return result.filter(id=user.id)

    def dehydrate(self, bundle):
        bundle = super(UserStatsResource, self).dehydrate(bundle)
        bundle.data['name'] = bundle.obj.username
        return bundle


class RequestResource(ModelResource):
    agency = fields.ForeignKey(AgencyResource, 'agency', null=True, full=True)
    contacts = fields.ToManyField(ContactResource, 'contacts', full=True)
    tags = fields.ToManyField(TagResource, 'tags', full = True)

    class Meta:
        queryset = Request.objects.all()
        resource_name = 'request'
        allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'put', 'patch']
        authorization = Authorization()
        always_return_data = True
        filtering = {
            'id': ALL,
            'status': ALL,
            'tags' : ALL_WITH_RELATIONS,
        }
        
    def build_filters(self, filters=None):
        if filters is None:
            filters = {}
        orm_filters = super(RequestResource, self).build_filters(filters)
        if 'groups__name' in filters:
            orm_filters['groups__name'] = filters['groups__name']
        if 'groups__id' in filters:
            orm_filters['groups__id'] = filters['groups__id']

        if 'status__in' in orm_filters:
            query = orm_filters['status__in'][0].split(",")
            orm_filters['status__in'] = query
        return orm_filters

    def apply_filters(self, request, applicable_filters):
        filters = applicable_filters
        if 'groups__name' in filters:
            groups_name = filters.pop('groups__name')
        else:
            groups_name = None

        if 'groups__id' in filters:
            groups_id = filters.pop('groups__id')
        else:
            groups_id = None

        filtered = super(RequestResource, self).apply_filters(request, applicable_filters)
        group = None

        if groups_id:
            try:
                group = Group.objects.get(id = groups_id)
            except:
                pass

        if groups_name:
            try:
                group = Group.objects.get(name = groups_name)
            except:
                pass
        if group and request.user.has_perm(UserProfile.get_permission_name('view'), group):
            return get_objects_for_group(group, Request.get_permissions_path('view')).filter(~Q(status='X'))
        return filtered


    def get_object_list(self, request):
        #getting lazyload error if we don't take some action to load the user obj
        print request.user.id
        obj_list = Request.objects.for_user(request.user)
        try:
            if request.GET.get("authored", None) and request.GET.get("authored").lower() in ("yes", "true", "t", "1", "True"):
                return obj_list.filter(author=request.user)
            return obj_list
        except Exception as e:
            #probably an anon user
            logger.info(e)
            return Request.public.all()
            #return obj_list.filter(private=False)

    def dehydrate(self, bundle):
        for ct in bundle.data['contacts']:
            ct.data['selected'] = True
        bundle.data['generated_text'] = bundle.obj.letter_html
        bundle.data['can_send'] = bundle.obj.can_send
        bundle.data['sent'] = bundle.obj.sent
        bundle.data['title'] = bundle.obj.get_title_string
        bundle.data['status_color'] = bundle.obj.get_status_color
        bundle.data['privacy_str'] = bundle.obj.get_privacy_string
        bundle.data['due_date_str'] = bundle.obj.get_due_date_string
        bundle.data['date_added_str'] = bundle.obj.get_date_added_string
        bundle.data['date_updated_str'] = bundle.obj.get_date_updated_string
        bundle.data['agency_str'] = bundle.obj.get_agency_string
        bundle.data['gov_str'] = bundle.obj.get_government_string
        bundle.data['tag_str'] = bundle.obj.get_tags_string
        bundle.data['detail_url'] = bundle.obj.get_detail_url
        bundle.data['status_str'] = bundle.obj.get_status
        bundle.data['id'] = bundle.obj.id
        bundle.data['request_download_url'] = bundle.obj.printed.get_public_url if bundle.obj.printed is not None else ""
        bundle.data['attachments'] = [{'id': atch.pk, 'filename' : atch.get_filename, 'url' : atch.url} for atch in bundle.obj.attachments.all()]
        return bundle

    def hydrate(self, bundle):
        return bundle

    def obj_update(self, bundle, **kwargs):
        data = bundle.data
        bundle.obj = Request.objects.get(id=bundle.data['id'])
        can_edit = bundle.request.user.has_perm(Request.get_permission_name('edit'), bundle.obj)
        if not can_edit:
            raise ImmediateHttpResponse(HttpBadRequest("It appears you don't have permission to change this request."))

        if 'status' in bundle.data:
            status = bundle.data['status']
            del bundle.data['status']
            if status:
                bundle.obj.set_status(status)
        attachments = []
        if 'attachments' in bundle.data:
            for atch in data['attachments']:
                attachment = Attachment.objects.get(id=atch['id'])
                attachments.append(attachment)
            bundle.obj.attachments = attachments
            del data['attachments']
        for field in ['title', 'free_edit_body', 'private', 'text', 'phone_contact', 'prefer_electornic', 'max_cost', 'fee_waiver']:
            if field in data:
                try:
                    setattr(bundle.obj, field, data[field])
                except Exception as e:
                    logger.info('error setting field %s e=%s' % (field, e))
            else:
                logger.info('field %s not allowed' % field)
        contacts = associate_contacts(bundle, data)

        bundle.obj.contacts = contacts
        bundle.obj.save()
        #bundle.data['can_send'] = bundle.obj.can_send

        if 'generate_pdf' in bundle.data:
            bundle.obj.create_pdf_body()

        if 'do_send' in bundle.data and bundle.data['do_send']:
            #obj sent property will reflect whether it has been sent
            bundle.obj.send()
            #bundle.data['sent'] = bundle.obj.sent
        return bundle

    def obj_create(self, bundle, **kwargs):
        try:
            attachments = []
            data = bundle.data
            contacts = associate_contacts(bundle, data)
            if 'attachments' in bundle.data:
                for atch in data['attachments']:
                    attachment = Attachment.objects.get(id=atch['id'])
                    attachments.append(attachment)
                del data['attachments']

            fields_to_use = {
                'author': bundle.request.user
            }
            for field in ['title', 'free_edit_body', 'private', 'text']:
                if field in data:
                    try:
                        #setattr(bundle.obj, field, data[field])
                        fields_to_use[field] = data[field]
                    except Exception as e:
                        logger.info('error setting field %s e=%s' % (field, e))
                else:
                    logger.info('field %s not allowed' % field)
            therequest = Request(**fields_to_use)
            therequest.date_added = datetime.now()
            therequest.save()
            therequest.contacts = contacts
            therequest.attachments = attachments
            therequest.save()
            bundle.obj = therequest
            
            logger.info("request %s created" % therequest.id)
        except Exception as e:
            logger.exception(e)
        return bundle
