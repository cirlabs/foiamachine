from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS
from tastypie import fields
from tastypie.paginator import Paginator

from django.core.exceptions import PermissionDenied
from django.db.models import Q, Count

from apps.agency.models import Agency
from apps.government.models import Government
from apps.government.api import GovernmentResource
from apps.contacts.api import ContactResource

from tastypie.authorization import Authorization#need?, DjangoAuthorization
from tastypie.authentication import Authentication
from tastypie.serializers import Serializer
from tastypie.validation import Validation
from tastypie.exceptions import BadRequest

from tastypie.cache import SimpleCache

from taggit.models import Tag
import logging

from datetime import datetime


logger = logging.getLogger('default')

# Hack mode for now 
def associate_government(bundle, data):
    try:
        government = Government.objects.get(id=data['government'])
        data['government'] = government
        return data
    except Exception as e:
        logger.info(e)
    return data


class AgencyAuthentication(Authentication):
    def is_authenticated (self, request):
        return request.user.is_authenticated()

class AgencyValidation(Validation):
    def is_valid(self, bundle, request=None):
        if not bundle.data:
            return 'No data submitted'
        if not bundle.data['government']:
            return 'Agency not associated with any government'
        if not bundle.data['name']:
            return 'Agency requires a name'
        if 'created' in bundle.data:
            return {}
        if Agency.objects.filter(name=bundle.data['name'], government__id=bundle.data['government'], hidden=False).count() > 0:
            return 'An agency with that name and government already exists, please select a different government or use a different name.'
        return {}

class AgencyPaginator(Paginator):

    def get_next(self, limit, offset, count):
        # See http://django-tastypie.readthedocs.org/en/latest/paginator.html
        count = 2 ** 64
        return super(AgencyPaginator, self).get_next(limit, offset, count)

    def get_count(self):
        return None

def agency_is_valid(bundle, request=None):
    if not bundle.data:
        return 'No data submitted'
    if not bundle.data['government']:
        return 'Agency not associated with any government'
    if not bundle.data['name']:
        return 'Agency requires a name'
    if 'created' in bundle.data:
        return ''
    if 'id' in bundle.data.keys():
        if Agency.objects.filter(name=bundle.data['name'], government__id=bundle.data['government'], hidden=False).exclude(id=bundle.data['id']).count() > 0:
            return 'An agency with that name and government already exists, please select a different government or use a different name.'
    else:
        if Agency.objects.filter(name=bundle.data['name'], government__id=bundle.data['government'], hidden=False).count() > 0:
            return 'An agency with that name and government already exists, please select a different government or use a different name.'
    return ''

class SimpleHTTPCache(SimpleCache):
    """
    """
    def cache_control(self):
        return {
            'no_cache': False,
            'max_age': 300,
        }

    def set(self, key, value, timeout=300):
        data = self._load()
        data[key] = value
        self._save(data)

    def get(self, key):
        data = self._load()
        return data.get(key, None)


class AgencyResource(ModelResource):
    contacts = fields.ToManyField(ContactResource, 'contacts')
    government = fields.ForeignKey(GovernmentResource, 'government')

    class Meta:
        queryset = Agency.objects.order_by('-created').prefetch_related("government", "creator")
        ordering = ['government','name',]
        resource_name = 'agency'
        allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'put']
        #authorization = Authorization()
        #authentication = AgencyAuthentication()
        validation = AgencyValidation()
        always_return_data = True
        paginator_class = AgencyPaginator
        filtering = {
            'id': ALL,
            'name' : ALL,
            'government' : ALL_WITH_RELATIONS,
            'tags': ALL_WITH_RELATIONS,
            'contacts': ALL_WITH_RELATIONS,
            'pub_contact_cnt': ALL
        }

    def alter_list_data_to_serialize(self, request, data):
        result = super(AgencyResource, self).alter_list_data_to_serialize(request, data)
        data['meta']['total_count'] = self.current_data_len
        return result


    def get_object_list(self, request):
        result = super(AgencyResource, self).get_object_list(request)
        return result

    def build_filters(self, filters=None):
        self.current_data_len = 100
        if filters is None:
            filters = {}

        orm_filters = super(AgencyResource, self).build_filters(filters)

        if 'query' in filters:
            query = filters['query']
            qset = (
                Q(name__icontains=query) |
                Q(government__name__icontains=query) 
            )
            orm_filters['query'] = qset

        if 'has_contacts' in filters:
            orm_filters['has_contacts'] = True

        if "show_can_edit" in filters:
            orm_filters['show_can_edit'] = True

        return orm_filters

    def apply_filters(self, request, filters):
        if 'query' in filters:
            query = filters.pop('query')
        else:
            query = None

        if 'has_contacts' in filters:
            has_contacts = filters.pop('has_contacts')
        else:
            has_contacts = None

        if 'show_can_edit' in filters:
            show_can_edit = filters.pop("show_can_edit")
        else:
            show_can_edit = None

        filtered = super(AgencyResource, self).apply_filters(request, filters)

        if query:
            filtered = filtered.filter(query)

        if has_contacts:
            filtered = filtered.annotate(num_contacts=Count('contacts')).filter(num_contacts__gte=1)

        #staff/supers can edit anything so no need to filter
        if show_can_edit and not request.user.is_staff and not request.user.is_superuser:
            filtered = filtered.filter(creator=request.user)
        self.current_data_len = filtered.count()
        return filtered
        
    def dehydrate(self, bundle):
        bundle.data['government'] = bundle.obj.government.id
        bundle.data['government_name'] = bundle.obj.government.name
        bundle.data['editor_contact_cnt'] = bundle.obj.editor_contact_cnt
        bundle.data['pub_contact_cnt'] = bundle.obj.pub_contact_cnt
        bundle.data['created_by'] = bundle.obj.creator.username if bundle.obj.creator is not None else "NA"
        return bundle
        
    def hydrate(self, bundle):
        return bundle

    def obj_update(self, bundle, **kwargs):
        try:
            data = bundle.data
            if len(agency_is_valid(bundle)) > 0:
                raise BadRequest(agency_is_valid(bundle))
            data = associate_government(bundle, data)
            agency = bundle.obj = Agency.objects.all_them().get(id=data['id'])
            user = bundle.request.user
            if not (bundle.request.user.is_superuser or bundle.request.user.is_staff or bundle.request.user == bundle.obj.creator):
                raise BadRequest("It appears you cannot edit this agency")
            for field in ['name', 'government', 'hidden']:
                if field in data:
                    setattr(agency, field, data[field])
            agency.save()
            return bundle
        except Exception as e:
            logger.exception(e)
            raise BadRequest (str(e))

    def obj_create(self, bundle, **kwargs):
        #for some reason agency validation is not being used...
        try:
            data = bundle.data
            if len(agency_is_valid(bundle)) > 0:
                raise BadRequest(agency_is_valid(bundle))
            data = associate_government(bundle, data)
            user = bundle.request.user
            if user.is_anonymous:
                user = None
            keyvals = {}
            for field in ['name', 'government', 'hidden']:
                if field in data:
                    keyvals[field] = data[field]
            theagency = Agency(**keyvals)
            theagency.save()
            theagency.creator = user
            theagency.save()
            bundle.obj = theagency

            logger.info("agency %s created" % theagency.id)
        except Exception as e:
            logger.exception(e)
        print bundle.obj
        return bundle
