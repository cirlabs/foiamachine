from apps.core.user_test_base import UserTestBase
from apps.agency.models import Agency
import json


class AgencyTesting(UserTestBase):

    
    def test_create_agency(self):
        self.create_agency()
        self.assertEqual(Agency.objects.all().count(), 1)

    def test_update_agency(self):
        self.create_agency()
        self.assertEqual(Agency.objects.all().count(), 1)

        self.userTwoAgencyData = self.agencyData.copy()
        self.userTwoAgencyData['name'] = 'uhhh'
        resp = self.api_client.post("/api/v1/agency/", format='json', data=self.userTwoAgencyData, authentication=self.get_credentials_other("yoko"))
        self.assertEqual(Agency.objects.all().count(), 2)

        #can't create two agencies with the same name
        resp = self.api_client.post("/api/v1/agency/", format='json', data=self.userTwoAgencyData, authentication=self.get_credentials_other("yoko"))
        self.assertEqual(Agency.objects.all().count(), 2)

        idd = Agency.objects.get(name=self.agencyData['name']).id
        self.editingAgencyData = self.agencyData.copy()
        self.editingAgencyData['id'] = idd
        self.editingAgencyData['name'] = 'An edited test agency'
        resp = self.api_client.put("/api/v1/agency/%s/" % idd, format='json', data=self.editingAgencyData, authentication=self.get_credentials())
        self.assertEqual(Agency.objects.get(name="An edited test agency").name, "An edited test agency")

        #only admin and creators can edit an agency name 
        self.agencyData['name'] = 'An edited test agency, updated by another'
        resp = self.api_client.put("/api/v1/agency/%s/" % idd, format='json', data=self.editingAgencyData, authentication=self.get_credentials_other('yoko'))
        self.assertEqual(Agency.objects.get(name="An edited test agency").name, "An edited test agency")

        self.userTwoAgencyData['name'] = 'An edited test agency, updated by another'
        self.userTwoAgencyData['id'] = Agency.objects.get(name="uhhh").id
        resp = self.api_client.put("/api/v1/agency/%s/" % self.userTwoAgencyData['id'], format='json', data=self.userTwoAgencyData, authentication=self.get_credentials_other('yoko'))
        #self.assertEqual(Agency.objects.get(name="An edited test agency, updated by another").name, 'An edited test agency, updated by another')

        self.editingAgencyData['name'] = 'An edited test agency, updated by an admin'
        resp = self.api_client.put("/api/v1/agency/%s/" % self.editingAgencyData['id'], format='json', data=self.editingAgencyData, authentication=self.get_credentials())
        self.assertEqual(Agency.objects.get(name="An edited test agency, updated by an admin").name, 'An edited test agency, updated by an admin')

        self.editingAgencyData['hidden'] = True
        resp = self.api_client.put("/api/v1/agency/%s/" % self.editingAgencyData['id'], format='json', data=self.editingAgencyData, authentication=self.get_credentials())
        self.assertEqual(Agency.objects.count(), 1)

        #what happens if we create an agency with the same name is one that exists and is deleted?        
        tmpAgencyData = self.agencyData.copy()
        del tmpAgencyData['hidden']
        tmpAgencyData['name'] = "An edited test agency, updated by an admin"
        resp = self.api_client.post("/api/v1/agency/", format='json', data=tmpAgencyData, authentication=self.get_credentials_other('ringo'))
        self.assertEqual(Agency.objects.count(), 2)

        #try to unhide but uh-oh, someone else already created a new agency with the same name and govt
        self.editingAgencyData['hidden'] = False
        resp = self.api_client.put("/api/v1/agency/%s/" % self.editingAgencyData['id'], format='json', data=self.editingAgencyData, authentication=self.get_credentials())
        self.assertEqual(Agency.objects.count(), 2)

        #must update the name first or switch government
        self.editingAgencyData['hidden'] = False
        self.editingAgencyData['name'] = "Someone took this agencies name"
        resp = self.api_client.put("/api/v1/agency/%s/" % self.editingAgencyData['id'], format='json', data=self.editingAgencyData, authentication=self.get_credentials())
        self.assertEqual(Agency.objects.count(), 3)
