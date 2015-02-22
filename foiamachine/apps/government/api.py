from tastypie.resources import ModelResource, Resource, ALL, ALL_WITH_RELATIONS
from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization#need?, DjangoAuthorization
from apps.government.models import Government, Statute, FeeExemptionOther
from tastypie.serializers import Serializer
from tastypie.exceptions import BadRequest, TastypieError, ApiFieldError
from tastypie.validation import Validation
from datetime import datetime

import bleach
import logging
logger = logging.getLogger('default')


class GovernmentValidation(Validation):
    def is_valid(self, bundle, request=None):
        if not bundle.request.user.is_staff:
            return "You do not have permission to edit this bundle"
        return {}
        
        
class GovernmentResource(ModelResource):
    class Meta:
        queryset = Government.objects.all()
        resource_name = 'governments'
        allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'put']
        #authorization = Authorization()
        #authentication = Authentication()
        filtering = {
            'name' : ALL,
            'slug' : ALL
        }
        

 
class StatuteAuthentication(Authentication):
    def is_authenticated (self, request):
        return request.user.is_authenticated()

class FeeExemptionResource(ModelResource):
    class Meta:
        queryset = FeeExemptionOther.objects.all().order_by('-created')
        resource_name = 'feeorexemption'
        allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'put']
        #authorization = Authorization()
        #authentication = StatuteAuthentication()
        filtering = {
            'id': ALL,
        }

    def get_object_list(self, request):
        if request.user.is_staff:
            return FeeExemptionOther.objects.all_them().order_by('-created')
        else:
            return FeeExemptionOther.objects.all().order_by('-created')


    def dehydrate(self, bundle):
        bundle.data['deleted'] = bundle.obj.deprecated is None
        bundle.data['can_edit'] = bundle.request.user.is_staff
        return bundle
  
    def hydrate(self, bundle):
        return bundle

    def obj_update(self, bundle, **kwargs):
        if not bundle.request.user.is_staff:
            return bundle
        try:
            data = bundle.data
            feeexemption = bundle.obj = FeeExemptionOther.objects.all_them().get(id=data['id'])
            for field in ['source', 'name', 'description', 'deleted', 'deprecated']:
                if field in data and field != 'deleted':
                    setattr(feeexemption, field, data[field])
                elif field == 'deleted' and field in data and data[field]:
                    feeexemption.deprecated = datetime.now()
            feeexemption.save()
            return bundle
        except Exception as e:
            logger.exception(e)
            raise BadRequest(str(e))

    def obj_create(self, bundle, **kwargs):
        if not bundle.request.user.is_staff:
            return bundle
        try:
            data = bundle.data
            statute = Statute.objects.get(id=data['statute_id'])
            del data['statute_id']#data for relationships
            del data['can_edit']#data for the template
            del data['type']#date for the template
            feeorexemption = FeeExemptionOther(**data)
            feeorexemption.save()
            bundle.obj = feeorexemption
            statute.fees_exemptions.add(feeorexemption)
            logger.info("feeorexemption %s created" % feeorexemption.id)
        except Exception as e:
            logger.exception(e)
        return bundle

class StatuteValidation(Validation):
    def is_valid(self, bundle, request=None):
        if not bundle.request.user.is_staff:
            return "You do not have permission to edit this statute"
        if not bundle.data:
            return "No data submitted"
        if not 'short_title' in bundle.data:
            return "Statute must have at least a distinct short title"
        short_title = bundle.data['short_title']
        if request and request.META and request.META['REQUEST_METHOD']=='POST' and Statute.objects.filter(short_title=short_title):
            
            return "A statute with that short title already exists."
        return {}

class StatuteResource(ModelResource):
    governments = fields.ToManyField(GovernmentResource, 'related_statutes', null = True, blank = True)

    class Meta:
        queryset = Statute.objects.all().order_by('-created')
        resource_name = 'statute'
        allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'put']
        #authorization = Authorization()
        #authentication = StatuteAuthentication()
        filtering = {
            'id': ALL,
        }
        validation = StatuteValidation()

    def get_object_list(self, request):
        if request.user.is_staff:
            return Statute.objects.all_them().order_by('-created')
        else:
            return Statute.objects.all().order_by('-created')

    def dehydrate(self, bundle):
        if 'governments' in bundle.data:
            bundle.data['governments'] = map(lambda x: {'id' : x.split("/")[-2]}, bundle.data['governments'])
        else:
            bundle.data['governments'] = []
        bundle.data['can_edit'] = True #TODO move this to check for a group
        bundle.data['deleted'] = bundle.obj.deprecated is None
        return bundle
  
    def hydrate(self, bundle):
        return bundle

    def obj_update(self, bundle, **kwargs):
        try:
            data = bundle.data
            statute = bundle.obj = Statute.objects.all_them().get(id=data['id'])
            for field in ['days_till_due', 'text', 'short_title', 'deleted', 'deprecated']:
                if field in data and field != 'deleted':
                    setattr(statute, field, data[field])
                elif field == 'deleted' and field in data and data[field]:
                    statute.deprecated = datetime.now()
            if 'governments' in data:
                governments = [Government.objects.get(id=id) for id in data['governments']]
                statute.related_statutes = governments
            statute.save()
            return bundle
        except Exception as e:
            logger.exception(e)
            raise BadRequest( str(e))
