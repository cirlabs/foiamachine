from django.conf import settings
from django.test import TestCase
from tastypie.test import ResourceTestCase, TestApiClient
from django.contrib.auth.models import User, Group
from apps.users.models import UserProfile
from apps.requests.models import Request
from apps.government.utils import load_states, load_statutes
from apps.government.models import Government, FeeExemptionOther, Statute
from apps.agency.models import Agency
from apps.contacts.models import Contact
import json

class UserTestBase(ResourceTestCase):

    def setUp(self):
        load_states()
        load_statutes()
        settings.DEBUG = True
        self.api_client = TestApiClient()
        self.get_credentials()
        #user creates all the groups and requests initially, user should always have edit perms unless another user takes that away
        self.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'secret')
        self.user.is_staff = True#someone has to be responsible
        self.user.save()
        self.usertwo = User.objects.create_user('yoko', 'yoko@thebeatles.com', 'secret')
        self.userthree = User.objects.create_user('ringo', 'ringo@thebeatles.com', 'secret')
        self.post_data = {
            'name': 'A TEST GROUP'
        }
        self.up, created = UserProfile.objects.get_or_create(user=self.user)
        self.uptwo, created = UserProfile.objects.get_or_create(user=self.usertwo)
        self.upthree, created = UserProfile.objects.get_or_create(user=self.userthree)
        self.groupJSON = None
        self.group = None
        self.request = None
        self.agency = None
        self.agencyJSON = None
        self.contact = None
        self.contactJSON = None
        self.government = None
        self.governmentJSON = None

    def tearDown(self):
        Request.objects.all().delete()
        Contact.objects.all_them().delete()
        Agency.objects.all_them().delete()
        FeeExemptionOther.objects.all_them().delete()
        Statute.objects.all_them().delete()
        Government.objects.all().delete()
        Group.objects.all().delete()
        User.objects.all().delete()



    def get_user_group(self, userToGet):
        #each user has their own group named after then which they are the sole member of
        for group in userToGet.groups.all():
            if group.name == userToGet.username:
                return group

    def create_group(self):
        #creates the default group and sets default json
        if self.groupJSON is not None:
            return self.groupJSON
        resp = self.api_client.post('/api/v1/group/', format='json', data=self.post_data, authentication=self.get_credentials())
        self.group = Group.objects.get(name=self.post_data['name'])
        self.groupJSON = json.loads(resp.content)
        return resp

    def get_group_json(self, group):
        #gets json for a group
        resp = self.api_client.get('/api/v1/group/%s/' % group.id, format='json', data={}, authentication=self.get_credentials())
        return json.loads(resp.content)

    def get_user_json(self, userToGet):
        users_resp = self.api_client.get("/api/v1/user/%s/" % userToGet.id, format='json', authentication=self.get_credentials())
        return json.loads(users_resp.content)

    def add_user_to_group(self, userToAdd):
        self.create_group()
        users = self.get_user_json(userToAdd)
        groupjson = self.groupJSON.copy()
        groupjson['users'].append(users)
        update_resp = self.api_client.put(self.groupJSON['resource_uri'], format='json', data=groupjson, authentication=self.get_credentials())

    def create_request(self, username=None):
        request_data = {
            'contacts': [],
            'free_edit_body': "<p>Something respectable, and testable!</p>",
            'private': True,
            'title': "test bangarang"
        }
        if username is None:
            self.api_client.post('/api/v1/request/', format='json', data=request_data, authentication=self.get_credentials())
        else:
            self.api_client.post('/api/v1/request/', format='json', data=request_data, authentication=self.get_credentials_other(username))
        self.request = Request.objects.get(title=request_data['title'])

    def get_credentials(self):
        #log in with self.user credentials
        result = self.api_client.client.login(username='john',
                                              password='secret')
        return result

    def get_credentials_other(self, username):
        #log in with self.user credentials
        result = self.api_client.client.login(username=username,
                                              password='secret')
        return result

    def create_agency(self):
        self.agencyData = {
            'government': Government.objects.get(name="United States of America").id,
            'name': "A test agency",
            'hidden': False
        }
        resp = self.api_client.post('/api/v1/agency/', format='json', data=self.agencyData, authentication=self.get_credentials())
        return resp

    def create_agency(self):
        if self.agencyJSON is not None:
            return self.agencyJSON
        self.agencyData = {
            'government': Government.objects.get(name="United States of America").id,
            'name': "A test agency",
            'hidden': False
        }
        resp = self.api_client.post('/api/v1/agency/', format='json', data=self.agencyData, authentication=self.get_credentials())
        self.agency = Agency.objects.get(name='A test agency')
        self.agencyJSON = json.loads(resp.content)
        return self.agencyJSON

    def create_contact(self, data=None):
        if self.agency is None:
            self.create_agency()
        if self.contactJSON is not None:
            return self.contactJSON
        self.contactData = {
            'first_name': "Testy",
            "last_name": "McTester",
            "dob": "1990-07-19",
            "notes": ["nothing much"],
            "phone_numbers": ["999-999-9999"],
            "titles": ["Public Information Officer"],
            "emails": ["testy@theoffice.com"],
            "addresses": ["1600 Penn. Washington DC 99999"],
            "agencyId": self.agency.id
        }
        if data is not None:
            self.contactData = data
        resp = self.api_client.post('/api/v1/contact/', format='json', data=self.contactData, authentication=self.get_credentials())
        self.contactJSON = json.loads(resp.content)
        self.contact = Contact.objects.get(first_name=self.contactData['first_name'], last_name=self.contactData['last_name'])
        return self.contactJSON

   