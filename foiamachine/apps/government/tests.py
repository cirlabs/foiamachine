from apps.core.user_test_base import UserTestBase
from apps.government.models import Government, Holiday, Statute, Nation, FeeExemptionOther, Language


import json


class GovernmentTesting(UserTestBase):

    def create_fee_exemption(self):
        self.feeExemptionData = {
            'can_edit': 'true',
            'description': "Enter a description",
            'name': "Enter a name",
            'source': "http://google.com",
            'statute_id': 56,
            'type': "fee",
            'typee': "F"
        }
        resp = self.api_client.post('/api/v1/feeorexemption/', format='json', data=self.feeExemptionData, authentication=self.get_credentials())

    def test_create_government(self):
        #we aren't creating governments via the api yet so make sure the laoder works
        self.assertEqual(Language.objects.all().count(), 1)
        self.assertEqual(Nation.objects.all().count(), 1)
        self.assertEqual(Statute.objects.all().count(), 53)
        self.assertEqual(Government.objects.all().count(), 52)

    def test_holidays(self):
        pass

    def test_fee_exemptions(self): 
        self.create_fee_exemption()
        self.assertEqual(FeeExemptionOther.objects.all().count(), 16)
        #only admins can create and edit fee/exmemptions etc
        resp = self.api_client.post('/api/v1/feeorexemption/', format='json', data=self.feeExemptionData, authentication=self.get_credentials_other('yoko'))
        self.assertEqual(FeeExemptionOther.objects.all().count(), 16)
        self.feeExemptionData['name'] = 'THE TEST FEE'
        idd = FeeExemptionOther.objects.all()[0].id
        self.feeExemptionData['id'] = idd
        update_resp = self.api_client.put('/api/v1/feeorexemption/%s/' % idd, format='json', data=self.feeExemptionData, authentication=self.get_credentials())
        self.assertEqual(FeeExemptionOther.objects.all()[0].name, 'THE TEST FEE')
        update_resp = self.api_client.put('/api/v1/feeorexemption/%s/' % idd, format='json', data=self.feeExemptionData, authentication=self.get_credentials_other('yoko'))
        self.assertEqual(FeeExemptionOther.objects.all()[0].name, 'THE TEST FEE')

        self.feeExemptionData['deleted'] = True
        update_resp = self.api_client.put('/api/v1/feeorexemption/%s/' % idd, format='json', data=self.feeExemptionData, authentication=self.get_credentials_other('yoko'))
        self.assertEqual(FeeExemptionOther.objects.all()[0].deleted, False)
        update_resp = self.api_client.put('/api/v1/feeorexemption/%s/' % idd, format='json', data=self.feeExemptionData, authentication=self.get_credentials())
        self.assertEqual(FeeExemptionOther.objects.all().count(), 15)


