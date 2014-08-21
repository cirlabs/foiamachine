from models import User, Group

from apps.requests.models import Request
from apps.users.models import UserProfile
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpBadRequest, HttpForbidden
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS, patch_cache_control
from guardian.core import ObjectPermissionChecker
from guardian.models import UserObjectPermission 
from guardian.shortcuts import assign_perm, remove_perm, get_groups_with_perms
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from tastypie.validation import Validation
from taggit.models import Tag
from tastypie import fields


from django.conf import settings
import logging

logger = logging.getLogger('default')

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        allowed_methods = ['get']
        detail_allowed_methods = ['get']
        authorization = Authorization()
        fields = ['id', 'first_name', 'last_name', 'username']
        max_limit = 0 # Just send them all
        limit = 0

    def get_object_list(self, request):
        return User.objects.all()

class GroupValidation(Validation):

    def is_valid(self, bundle, request=None):
        if not bundle.data:
            return "No data submitted"
        if not bundle.data['name']:
            return "Group must have a name"
        try:
            obj = Group.objects.get(name=bundle.data['name'])
            if obj.pk != int(bundle.data['id']):
                return "A group by that name already exists; try another"
        except:
            pass
        return {}


class GroupResource(ModelResource):
    users = fields.ToManyField(UserResource, 'user_set', full=True)

    class Meta:
        queryset = Group.objects.all()
        resource_name = 'group'
        allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        authorization = Authorization()
        max_limit = 0 # Just send them all
        limit = 0 # Just send them all
        always_return_data = True
        filtering = {
            'id': ALL
        }
        validation = GroupValidation()

    def get_object_list(self, request):
        try:
            user = request.user
            request_id = request.GET.get("request_id", None)
            user_id = request.GET.get("user_id", None)
            excluded = ['public', 'AnonymousUser']
            if request_id:
                req = Request.objects.get(id=request_id)
                if req.author == user:
                    excluded.append(user.username)
                if settings.DEBUG:
                    retval = get_groups_with_perms(req)
                else:
                    retval = get_groups_with_perms(req).exclude(name__in=excluded)
            elif user_id:
                excluded.append(user.username)
                retval = user.groups.all().exclude(name__in=excluded)
            else:
                if settings.DEBUG:
                    excluded.append(user.username)
                retval = Group.objects.all()
            return retval
        except Exception as e:
            logger.info(e)
            return []


    def dehydrate(self, bundle):
        if 'request_id' not in bundle.data.keys():
            bundle.data['request_id'] = bundle.request.GET.get("request_id", None)
        bundle.data['toggle_to_edit'] = bundle.request.user.has_perm(UserProfile.get_permission_name('edit'), bundle.obj)
        if bundle.data['request_id']:
            checker = ObjectPermissionChecker(bundle.obj)
            bundle.data['toggle_to_edit'] = checker.has_perm(Request.get_permission_name('edit'), Request.objects.get(id=bundle.data['request_id']))
        if not bundle.request.user.is_authenticated():
            bundle.data['can_edit'] = False
        bundle.data['can_edit'] = bundle.request.user.has_perm(UserProfile.get_permission_name('edit'), bundle.obj)
        bundle.data['type'] = 'group'
        for usr in bundle.data['users']:
            usr.data['toggle_to_edit'] = usr.obj.has_perm(UserProfile.get_permission_name('edit'), bundle.obj)
        return bundle

    def hydrate(self, bundle):
        return bundle

    def obj_create(self, bundle, **kwargs):
        #validator not being called
        data = bundle.data
        user = bundle.request.user
        thegroup = Group.objects.create(name=data['name'])
        thegroup.save()
        #creator of the group can edit by default
        assign_perm(UserProfile.get_permission_name('edit'), user, thegroup)
        assign_perm(UserProfile.get_permission_name('view'), user, thegroup)
        bundle.obj = thegroup

        # User always has edit permissions for group he made
        user.groups.add(thegroup)
        user.save()

        # Users are in the group
        if 'users' in data:
            thegroup.user_set = []
            users = [User.objects.get(pk=userid) for userid in data['users']]

            thegroup.user_set = users
        if 'request_id' in data and data['request_id']:
            req = Request.objects.get(id=data['request_id'])
            assign_perm(Request.get_permission_name('view'), thegroup, req)
        thegroup.save()


        return bundle

    def obj_update(self, bundle, **kwargs):
        data = bundle.data
        user = bundle.request.user
        bundle.obj = Group.objects.get(id=data['id'])
        if 'data' in data.keys():
            #if 'action' in data['data'].keys() and data['data']['action'] == 'chown':
            #we are associating, disassociating... assuming the USER is taking action here
            if 'request_id' in data.keys() and data['request_id']:
                req = Request.objects.get(id=data['request_id'])
                if 'action' in data['data'].keys() and req.author == bundle.request.user:
                    if data['data']['action'] == 'associate':
                        assign_perm(Request.get_permission_name('view'), bundle.obj, req)
                        bundle.data['data']['result'] = 'associated'
                    elif data['data']['action'] == 'disassociate':
                        remove_perm(Request.get_permission_name('view'), bundle.obj, req)
                        remove_perm(Request.get_permission_name('edit'), bundle.obj, req)
                        bundle.data['data']['result'] = 'disassociated'
                    elif data['data']['action'] == 'change-access':
                        #right now we are toggling between view and edit
                        checker = ObjectPermissionChecker(bundle.obj)
                        if checker.has_perm(Request.get_permission_name('view'), req) and not checker.has_perm(Request.get_permission_name('edit'), req):
                            assign_perm(Request.get_permission_name('edit'), bundle.obj, req)
                        elif user.has_perm(Request.get_permission_name('edit'), req):
                            remove_perm(Request.get_permission_name('edit'), bundle.obj, req)
                        else:
                            raise ImmediateHttpResponse(HttpForbidden("We couldn't determine the appropriate permissions to assign. Sorry."))
                else:
                    logger.info("%s tried to remove users from request %s owned by %s" % (bundle.request.user, req, req.author))
                    raise ImmediateHttpResponse(HttpBadRequest("It appears you don't have permission to change that user or group's permission."))
            else:
                can_edit = bundle.request.user.has_perm(UserProfile.get_permission_name('edit'), bundle.obj)
                if not can_edit:
                    raise ImmediateHttpResponse(HttpForbidden("It doesn't appear you can edit this group."))
                if 'action' in data['data'].keys() and data['data']['action'] == 'rename':
                    bundle.obj.name = data['name']
                    bundle.obj.save()
                if 'action' in data['data'].keys() and data['data']['action'] == 'chown' and 'user_id' in data['data'].keys() and data['data']['user_id']:
                    #change user permission on a group object
                    other_user = User.objects.get(id=data['data']['user_id'])
                    o_can_edit = other_user.has_perm(UserProfile.get_permission_name('edit'), bundle.obj)
                    if o_can_edit:
                        #toggled to view
                        remove_perm(UserProfile.get_permission_name('edit'), other_user, bundle.obj)
                    else:
                        #toggled to edit
                        assign_perm(UserProfile.get_permission_name('edit'), other_user, bundle.obj)
        else:
            '''
            NOTE about group permissions

            The creator of the requst is the only one who can share a request with other users and groups
            Otherwise the request could be shared with any number of people
            '''
            can_edit = bundle.request.user.has_perm(UserProfile.get_permission_name('edit'), bundle.obj)
            if not can_edit:
                raise ImmediateHttpResponse(HttpForbidden("It doesn't appear you can edit this group."))
            #we are adding or removing users to the group on the group page
            users = set([User.objects.get(pk=user['id']) for user in data['users']])
            existing_users = set([usr for usr in bundle.obj.user_set.all()])
            to_remove = existing_users - users
            #need to remove and set permissions here
            for usr in to_remove:
                remove_perm(UserProfile.get_permission_name('edit'), usr, bundle.obj)
                remove_perm(UserProfile.get_permission_name('view'), usr, bundle.obj)
            for usr in users:
                #users can view but not edit by default
                assign_perm(UserProfile.get_permission_name('view'), usr, bundle.obj)
            bundle.obj.user_set = users
            bundle.obj.save()
        data.pop('data', None)
        data.pop('request_id', None)

        return bundle

class TagValidation(Validation):
    def is_valid(self, bundle, request=None):
        if not bundle.data:
            return "No data submitted"
        if not 'name' in bundle.data or not bundle.data['name']:
            return "Tag must have a name"
        return {}
    

class TagResource(ModelResource):
    class Meta:
        queryset = Tag.objects.all()
        resource_name = 'tag'
        allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'put']
        authorization = Authorization()
        max_limit = 0 # Just send them all
        limit = 0 # Just send them all
        always_return_data = True
        filtering = {
            'id': ALL,
            'name': ALL
        }
        validation = TagValidation()

    def get_object_list(self, request):
        try:
            request_id = request.GET.get("request_id", None)
            if request_id:
                retval = Request.objects.get(id=request_id).tags.all()
            else:
                '''
                TODO: add a can_edit field to the tag class (if possible) so we can hide any buttons / functionality that would
                give a user the impression they can edit a tag when they cannot
                '''
                try:
                    up = UserProfile.objects.get(user=request.user)
                    retval = up.tags.all()
                except:
                    retval = Tag.objects.all() 
            return retval
        except Exception as e:
            logger.info(e)
            return []


    def dehydrate(self, bundle):
        if 'request_id' not in bundle.data.keys():
            bundle.data['request_id'] = bundle.request.GET.get("request_id", None)

        if bundle.request.user.is_authenticated():            
            user = bundle.request.user
            up = UserProfile.objects.get(user=user)
            bundle.data['can_edit'] = (up.tags.filter(id=bundle.data['id']).count() > 0)
        else:
            bundle.data['can_edit'] = False
        return bundle

    def hydrate(self, bundle):
        return bundle

    def obj_create(self, bundle, **kwargs):
        try:
            data = bundle.data
            user = bundle.request.user
            up = UserProfile.objects.get(user=user)
            if 'data' in data.keys():
                #tags need to be added to an object, this can be expanded to other objects like contacts
                if 'request_id' in data.keys():
                    req = Request.objects.get(id=data['request_id'])
                    up.tags.add(data['name'])
                    obj = up.tags.get(name=data['name'])
                    req.tags.add(data['name'])
                    bundle.data['data']['result'] = 'created'
                    bundle.obj = obj
                if 'request_ids' in data.keys():
                    requests = Request.objects.filter(id__in=data['request_ids'])
                    for req in requests:
                        can_edit = user.has_perm(Request.get_permission_name('view'), req)

                        if not can_edit:
                            logger.info("%s tried to add/edit/rename tags from request %s owned by %s" % (bundle.request.user, req, req.author))
                            raise ImmediateHttpResponse(HttpForbidden("It appears you do not have permissions to add or remove tags here."))
                    bundle.data['data']['result'] = 'created'
                    up.tags.add(data['name'])
                    obj = up.tags.get(name=data['name'])
                    bundle.obj = obj
                    for req in requests:
                        req.tags.add(data['name'])
                    
        except Exception as e:
            logger.exception(e)
        return bundle

    def obj_update(self, bundle, **kwargs):
        '''
        NOTES about permissions on tags

        Tags should be scoped to the UserProfile.tags so multiple users can have tags with the same name
        If a tag is not in UserProfile.tags then it wasn't created by that user
        Any user with edit access to the request should be able to add/remove a tag
        We should check that a request doesn't already have a tag of the same name so a request can't have two different tags of the same name
        BUT only the person who created a tag should be able to rename it
        (user1 has a tag phase1, user2 has a tag phase2, user2's phase1 tag shouldn't be changed if user1 updates his or her tag name)
        '''
        data = bundle.data
        user = bundle.request.user
        up = UserProfile.objects.get(user=user)
        bundle.obj = Group.objects.get(id=data['id'])
        if 'data' in data.keys():
            if 'action' in data['data'].keys() and 'request_ids' in data.keys():
                # For bulk tagging
                requests = Request.objects.filter(id__in=data['request_ids'])
                for req in requests:
                    can_edit = user.has_perm(Request.get_permission_name('view'), req)

                    if not can_edit:
                        logger.info("%s tried to add/edit/rename tags from request %s owned by %s" % (bundle.request.user, req, req.author))
                        raise ImmediateHttpResponse(HttpForbidden("It appears you do not have permissions to add or remove tags here."))

                for req in requests:
                    # OK, they have permission, now let's actually do it

                    if data['data']['action'] == 'associate':
                        obj = up.tags.get(id=data['id'])
                        tags = req.tags.filter(name=data['name'])
                        if tags:
                            # Already tagged like that
                            for tag in tags:
                                if tag.id != obj.id:
                                    # Already tagged by another user
                                    raise ImmediateHttpResponse(HttpForbidden("A tag by this name is already associated with one of these requests by another user."))
                        else:
                            # Tag it now
                            req.tags.add(obj)

                    elif data['data']['action'] == 'disassociate':
                        req.tags.remove(data['name'])

                bundle.obj = Tag.objects.get(id=data['id'])

                        
                        





                    

            if 'request_id' in data.keys():
                req = Request.objects.get(id=data['request_id'])
                can_edit = user.has_perm(Request.get_permission_name('view'), req)
                if 'action' in data['data'].keys() and can_edit:
                    if data['data']['action'] == 'associate':
                        if req.tags.filter(name=data['name']).count() > 0:
                            raise ImmediateHttpResponse(HttpForbidden("A tag by this name is already associated with this request."))
                        obj = up.tags.get(id=data['id'])
                        req.tags.add(obj)
                    elif data['data']['action'] == 'disassociate':
                        req.tags.remove(data['name'])
                    #refresh the obj for backbone to update
                    bundle.obj = Tag.objects.get(id=data['id'])
                else:
                    logger.info("%s tried to add/edit/rename tags from request %s owned by %s" % (bundle.request.user, req, req.author))
                    raise ImmediateHttpResponse(HttpForbidden("It appears you do not have permissions to add or remove tags here."))
            #action independent of request
            if data['data']['action'] == 'rename':
                usertags = up.tags.all()
                if usertags.filter(id=data['id']).count() == 0:
                    #not my tag, presumably
                    raise ImmediateHttpResponse(HttpForbidden("It appears you do not have permissions to edit this tag."))
                elif usertags.filter(name=data['name']).count() < 2:
                    tag = Tag.objects.get(id=data['id'])
                    tag.name = data['name']
                    tag.save()
                    bundle.obj = tag
                else:
                    raise ImmediateHttpResponse(HttpForbidden("An error occurred while trying to modify this tag."))
        return bundle
