from apps.core.user_test_base import UserTestBase
from apps.requests.models import Request
from apps.users.models import UserProfile
from guardian.shortcuts import get_objects_for_group
import json

class GroupPermissions(UserTestBase):

    def test_add_user_to_group(self):
        self.add_user_to_group(self.usertwo)
        self.assertEqual(self.usertwo.groups.filter(name=self.post_data['name']).count(), 1)
        #user who created a group has ownership over it
        self.assertEqual(self.user.has_perm(UserProfile.get_permission_name('edit'), self.group), True)
        self.assertEqual(self.usertwo.has_perm(UserProfile.get_permission_name('edit'), self.group), False)
        self.assertEqual(self.user.has_perm(UserProfile.get_permission_name('view'), self.group), True)
        self.assertEqual(self.usertwo.has_perm(UserProfile.get_permission_name('view'), self.group), True)

        #user two didn't create the group but is part of it, usertwo shouldn't be able to add userthree to the group in this case
        self.get_credentials_other(self.usertwo.username)
        users = self.get_user_json(self.userthree)
        groupjson = self.groupJSON.copy()
        groupjson['users'].append(users)
        update_resp = self.api_client.put(groupjson['resource_uri'], format='json', data=groupjson, authentication=self.get_credentials_other(self.usertwo.username))
        self.assertEqual(self.userthree.groups.filter(name=self.post_data['name']).count(), 0)

        #remove a user from the group
        groupjson['users'] = [self.get_user_json(self.user)]
        update_resp = self.api_client.put(groupjson['resource_uri'], format='json', data=groupjson, authentication=self.get_credentials())
        self.assertEqual(self.usertwo.groups.filter(name=self.post_data['name']).count(), 0)
        self.assertEqual(self.user.has_perm(UserProfile.get_permission_name('edit'), self.group), True)
        self.assertEqual(self.user.has_perm(UserProfile.get_permission_name('view'), self.group), True)
        self.assertEqual(self.usertwo.has_perm(UserProfile.get_permission_name('edit'), self.group), False)
        self.assertEqual(self.usertwo.has_perm(UserProfile.get_permission_name('view'), self.group), False)

    def test_change_user_group_perms(self):
        self.add_user_to_group(self.usertwo)
        self.assertEqual(self.usertwo.groups.filter(name=self.post_data['name']).count(), 1)
        groupjson = self.groupJSON.copy()
        groupjson['data'] = {'action': 'chown', 'user_id': self.usertwo.id}
        update_resp = self.api_client.put(groupjson['resource_uri'], format='json', data=groupjson, authentication=self.get_credentials())
        self.assertEqual(self.usertwo.has_perm(UserProfile.get_permission_name('edit'), self.group), True)
        self.assertEqual(self.userthree.has_perm(UserProfile.get_permission_name('edit'), self.group), False)
        self.assertEqual(self.user.has_perm(UserProfile.get_permission_name('edit'), self.group), True)
        groupjson = self.groupJSON.copy()
        groupjson['data'] = {'action': 'chown', 'user_id': self.userthree.id}

        #attempt to grant permissions without using an editor user
        update_resp = self.api_client.put(groupjson['resource_uri'], format='json', data=groupjson, authentication=self.get_credentials_other(self.userthree.username))
        self.assertEqual(self.usertwo.has_perm(UserProfile.get_permission_name('edit'), self.group), True)
        self.assertEqual(self.userthree.has_perm(UserProfile.get_permission_name('edit'), self.group), False)
        self.assertEqual(self.user.has_perm(UserProfile.get_permission_name('edit'), self.group), True)

        #grant permissions using an editor user
        update_resp = self.api_client.put(groupjson['resource_uri'], format='json', data=groupjson, authentication=self.get_credentials_other(self.usertwo.username))
        self.assertEqual(self.usertwo.has_perm(UserProfile.get_permission_name('edit'), self.group), True)
        self.assertEqual(self.userthree.has_perm(UserProfile.get_permission_name('edit'), self.group), True)
        self.assertEqual(self.user.has_perm(UserProfile.get_permission_name('edit'), self.group), True)

        #take away edit permissions
        update_resp = self.api_client.put(groupjson['resource_uri'], format='json', data=groupjson, authentication=self.get_credentials_other(self.usertwo.username))
        self.assertEqual(self.usertwo.has_perm(UserProfile.get_permission_name('edit'), self.group), True)
        self.assertEqual(self.userthree.has_perm(UserProfile.get_permission_name('edit'), self.group), False)
        self.assertEqual(self.user.has_perm(UserProfile.get_permission_name('edit'), self.group), True)

    def test_create_group(self):
        self.assertHttpCreated(self.create_group())
        self.assertEqual(self.user.groups.filter(name=self.post_data['name']).count(), 1)

    def test_add_user_to_request(self):
        self.create_group()
        self.create_request()
        self.assertEqual(self.user.has_perm(Request.get_permission_name('edit'), self.request), True)
        self.assertEqual(self.user.has_perm(Request.get_permission_name('view'), self.request), True)
        self.assertEqual(self.usertwo.has_perm(Request.get_permission_name('view'), self.request), False)
        self.assertEqual(self.usertwo.has_perm(Request.get_permission_name('edit'), self.request), False)
        self.assertEqual(self.userthree.has_perm(Request.get_permission_name('edit'), self.request), False)
        self.assertEqual(self.userthree.has_perm(Request.get_permission_name('view'), self.request), False)


        usergroup = self.get_user_group(self.userthree)
        groupjson = self.get_group_json(usergroup).copy()
        groupjson['data'] = {'action': 'associate'}
        groupjson['request_id'] = self.request.id

        update_resp = self.api_client.put("/api/v1/group/%s/" % usergroup.id, format='json', data=groupjson, authentication=self.get_credentials())

        self.assertEqual(self.userthree.has_perm(Request.get_permission_name('edit'), self.request), False)
        self.assertEqual(self.userthree.has_perm(Request.get_permission_name('view'), self.request), True)
        self.assertEqual(self.usertwo.has_perm(Request.get_permission_name('view'), self.request), False)
        self.assertEqual(self.usertwo.has_perm(Request.get_permission_name('edit'), self.request), False)
        self.assertEqual(self.user.has_perm(Request.get_permission_name('edit'), self.request), True)
        self.assertEqual(self.user.has_perm(Request.get_permission_name('view'), self.request), True)

        #test that users can query for request
        resp = self.api_client.get('/api/v1/request/%s/' % self.request.id, format='json', data={}, authentication=self.get_credentials_other(self.userthree.username))
        requestjson = json.loads(resp.content).copy()
        self.assertEqual(requestjson['id'], self.request.id)

        requestjson['title'] = 'TEST UPDATING THE TITLE'
        self.api_client.put('/api/v1/request/%s/' % self.request.id, format='json', data=requestjson, authentication=self.get_credentials_other(self.userthree.username))
        self.assertEqual(Request.objects.get(id=self.request.id).title, 'test bangarang')

        #only get the requests I created
        resp = self.api_client.get('/api/v1/request/', format='json', data={'authored': True}, authentication=self.get_credentials_other(self.userthree.username))
        requestjson = json.loads(resp.content).copy()
        self.assertEqual(len(requestjson['objects']), 0)

        resp = self.api_client.get('/api/v1/request/', format='json', data={'authored': ''}, authentication=self.get_credentials_other(self.userthree.username))
        requestjson = json.loads(resp.content).copy()
        self.assertEqual(len(requestjson['objects']), 1)

        #ensure people can't view it
        resp = self.api_client.get('/api/v1/request/%s/' % self.request.id, format='json', data={}, authentication=self.get_credentials_other(self.usertwo.username))
        self.assertEqual(resp.content, '')

        groupjson = self.get_group_json(usergroup).copy()
        groupjson['data'] = {'action': 'change-access'}
        groupjson['request_id'] = self.request.id

        update_resp = self.api_client.put("/api/v1/group/%s/" % usergroup.id, format='json', data=groupjson, authentication=self.get_credentials())

        self.assertEqual(self.userthree.has_perm(Request.get_permission_name('edit'), self.request), True)
        self.assertEqual(self.userthree.has_perm(Request.get_permission_name('view'), self.request), True)
        self.assertEqual(self.usertwo.has_perm(Request.get_permission_name('view'), self.request), False)
        self.assertEqual(self.usertwo.has_perm(Request.get_permission_name('edit'), self.request), False)
        self.assertEqual(self.user.has_perm(Request.get_permission_name('edit'), self.request), True)
        self.assertEqual(self.user.has_perm(Request.get_permission_name('view'), self.request), True)


        #test that users can query for request
        resp = self.api_client.get('/api/v1/request/%s/' % self.request.id, format='json', data={}, authentication=self.get_credentials_other(self.userthree.username))
        requestjson = json.loads(resp.content).copy()
        self.assertEqual(requestjson['id'], self.request.id)

        requestjson['title'] = 'TEST UPDATING THE TITLE'
        self.api_client.put('/api/v1/request/%s/' % self.request.id, format='json', data=requestjson, authentication=self.get_credentials_other(self.userthree.username))
        self.assertEqual(Request.objects.get(id=self.request.id).title, 'TEST UPDATING THE TITLE')

        groupjson = self.get_group_json(usergroup).copy()
        groupjson['data'] = {'action': 'disassociate'}
        groupjson['request_id'] = self.request.id

        update_resp = self.api_client.put("/api/v1/group/%s/" % usergroup.id, format='json', data=groupjson, authentication=self.get_credentials())
        self.assertEqual(self.userthree.has_perm(Request.get_permission_name('edit'), self.request), False)
        self.assertEqual(self.userthree.has_perm(Request.get_permission_name('view'), self.request), False)
        self.assertEqual(self.usertwo.has_perm(Request.get_permission_name('view'), self.request), False)
        self.assertEqual(self.usertwo.has_perm(Request.get_permission_name('edit'), self.request), False)
        self.assertEqual(self.user.has_perm(Request.get_permission_name('edit'), self.request), True)
        self.assertEqual(self.user.has_perm(Request.get_permission_name('view'), self.request), True)

    def test_add_request_to_group(self):
        '''
        Anyone in a group can edit the request
        '''
        self.create_group()
        self.create_request()
        self.assertEqual(self.user.has_perm(Request.get_permission_name('edit'), self.request), True)
        self.assertEqual(self.usertwo.has_perm(Request.get_permission_name('edit'), self.request), False)
        self.assertEqual(self.usertwo.has_perm(Request.get_permission_name('view'), self.request), False)

        #show that the API won't return the request for a user not in teh group
        resp = self.api_client.get('/api/v1/request/%s/' % self.request.id, format='json', data={}, authentication=self.get_credentials_other(self.usertwo.username))
        self.assertEqual(resp.content, '')
        resp = self.api_client.get('/api/v1/request/%s/' % self.request.id, format='json', data={}, authentication=self.get_credentials())
        requestjson = json.loads(resp.content).copy()
        self.assertEqual(requestjson['id'], self.request.id)

        self.add_user_to_group(self.usertwo)

        groupjson = self.groupJSON.copy()
        groupjson['data'] = {'action': 'associate'}
        groupjson['request_id'] = self.request.id

        update_resp = self.api_client.put(self.groupJSON['resource_uri'], format='json', data=groupjson, authentication=self.get_credentials())
        self.assertEqual(self.user.has_perm(Request.get_permission_name('edit'), self.request), True)
        self.assertEqual(self.usertwo.has_perm(Request.get_permission_name('edit'), self.request), False)
        self.assertEqual(self.usertwo.has_perm(Request.get_permission_name('view'), self.request), True)

        #user two can now view a request,  has to look through group requests function
        data = {'groups__id': self.groupJSON['id']}
        resp = self.api_client.get('/api/v1/request/%s/' % self.request.id, format='json', data=data, authentication=self.get_credentials_other(self.usertwo.username))
        requestjson = json.loads(resp.content).copy()
        self.assertEqual(requestjson['id'], self.request.id)

        #user can view a request, not edit
        resp = self.api_client.get('/api/v1/request/%s/' % self.request.id, format='json', data={}, authentication=self.get_credentials())
        requestjson = json.loads(resp.content).copy()
        requestjson['title'] = 'TEST UPDATING THE TITLE'
        #no content on puts for request
        #user two should not be able to change a request (they only have view for this group)
        self.api_client.put('/api/v1/request/%s/' % self.request.id, format='json', data=requestjson, authentication=self.get_credentials_other(self.usertwo.username))
        self.assertEqual(self.request.title, 'test bangarang')
        self.api_client.put('/api/v1/request/%s/' % self.request.id, format='json', data=requestjson, authentication=self.get_credentials())
        #for some reason self.request is not reflecting the change (stale?)
        self.assertEqual(Request.objects.get(id=self.request.id).title, 'TEST UPDATING THE TITLE')

        #ensure that we can list objects in a group
        self.create_request()
        resp = self.api_client.get('/api/v1/request/', format='json', data=data, authentication=self.get_credentials_other(self.usertwo.username))
        requestjson = json.loads(resp.content).copy()
        self.assertEqual(len(requestjson['objects']), 1)
        #make sure we only get requests for the group for this user (he should have 2 or more requests at this point)
        resp = self.api_client.get('/api/v1/request/', format='json', data=data, authentication=self.get_credentials())
        requestjson = json.loads(resp.content).copy()
        self.assertEqual(len(requestjson['objects']), 1)
        resp = self.api_client.get('/api/v1/request/', format='json', data={}, authentication=self.get_credentials())
        requestjson = json.loads(resp.content).copy()
        self.assertEqual(len(requestjson['objects']), 2)
        #ensure users who aren't part of the group can't access those requests
        resp = self.api_client.get('/api/v1/request/', format='json', data=data, authentication=self.get_credentials_other(self.userthree.username))
        requestjson = json.loads(resp.content).copy()
        self.assertEqual(len(requestjson['objects']), 0)

