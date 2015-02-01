from apps.core.user_test_base import UserTestBase
from apps.contacts.models import Contact
from apps.contacts.utils import *
from apps.core.models import EmailAddress
from apps.government.models import Government
from apps.agency.models import Agency

import json


class ContactTesting(UserTestBase):

    def test_set_new_agency(self):
        govt = Government.objects.all()[0]
        agency, created = Agency.objects.get_or_create(name="California Department of Public Health", government=govt)
        contact, created = Contact.objects.get_or_create(first_name='default', middle_name='', last_name='contact')
        contact.save()
        contact.add_email('cdph.internetadmin@cdph.ca.gov')
        agency.contacts.add(contact)
        contact, created = Contact.objects.get_or_create(first_name='Ken', middle_name='', last_name='August')
        contact.save()
        contact.add_email('ken.august@cdph.ca.gov')
        agency.contacts.add(contact)


        newagency, created = Agency.objects.get_or_create(name="A new agency", government=govt)

        contact.set_new_agency(newagency)

        #for ctct in agency.contacts.all():
        #    self.assertNotEqual(ctct.id, contact.id)

        agencyContactIds = map(lambda x: x.id, newagency.contacts.all())

        #self.assertEqual(contact.id in agencyContactIds, True)

    def test_create_contact(self):
        self.create_contact()
        self.assertEqual(Contact.objects.all().count(), 1)

        #create a second agency for comparison
        self.userTwoAgencyData = self.agencyData.copy()
        self.userTwoAgencyData['name'] = 'uhhh'
        resp = self.api_client.post("/api/v1/agency/", format='json', data=self.userTwoAgencyData, authentication=self.get_credentials_other("yoko"))

        self.editingContactData = self.contactData.copy()
        self.editingContactData['agencyId'] = Agency.objects.get(name='uhhh').id
        #emails are created when an email is sent to FOIA Machine so we dropped the unique constraint
        resp = self.api_client.post('/api/v1/contact/', format='json', data=self.editingContactData, authentication=self.get_credentials_other('yoko'))
        self.assertEqual(Contact.objects.all().count(), 2)
        self.assertEqual(EmailAddress.objects.all().count(), 1)

        #anyone can indeed create a contact even if some of the details are the same
        self.otherContactData = self.contactData.copy()
        self.otherContactData['first_name'] = "Brother"
        self.otherContactData['last_name'] = "Man"
        self.otherContactData['emails'] = ['brother@man.com']
        resp = self.api_client.post('/api/v1/contact/', format='json', data=self.otherContactData, authentication=self.get_credentials_other('yoko'))
        #ensure we have the same number of contacts
        self.assertEqual(EmailAddress.objects.all().count(), 2)
        self.assertEqual(Contact.objects.all().count(), 3)

        #set up editing
        self.otherContact = Contact.objects.get(first_name='Brother', last_name="Man")
        self.editingContactData = self.contactData.copy()
        self.editingContactData['id'] = self.contact.id
        self.otherContactData['id'] = self.otherContact.id

        #ringo can't edit yoko's contact
        self.otherContactData['emails'] = ['brotherman@anotheragency.com']
        resp = self.api_client.put("/api/v1/contact/%s/" % self.otherContact.id, data=self.otherContactData, authentication=self.get_credentials_other('ringo'))
        self.assertEqual(self.otherContact.emails.all()[0].content, 'brother@man.com') 
        self.assertEqual(EmailAddress.objects.all().count(), 2)

        #but the admin can
        self.otherContactData['first_name'] = 'Mr. Brother' 
        resp = self.api_client.put("/api/v1/contact/%s/" % self.otherContact.id, data=self.otherContactData, authentication=self.get_credentials())
        self.otherContact = Contact.objects.get(first_name='Mr. Brother', last_name="Man")
        self.assertEqual(self.otherContact.first_name, 'Mr. Brother')

        resp = self.api_client.put("/api/v1/contact/%s/" % self.otherContact.id, data=self.otherContactData, authentication=self.get_credentials_other('yoko'))
        self.otherContact = Contact.objects.get(first_name='Mr. Brother', last_name="Man")
        self.assertEqual(self.otherContact.emails.all()[0].content, 'brotherman@anotheragency.com') 
        #ensure a new email wasn't created
        self.assertEqual(EmailAddress.objects.all_them().count(), 2)

        self.otherContactData['hidden'] = True
        #temp build fix, email constraints were removed... fix is to seperate them from the emails created when an email is received.
        del self.otherContactData['emails']#anything sent will be updated so the API thinks this is a duplicate email address and throws an address
        #resp = self.api_client.put("/api/v1/contact/%s/" % self.otherContact.id, data=self.otherContactData, authentication=self.get_credentials_other('yoko'))
        #self.assertEqual(Contact.objects.all().count(), 2)
        #self.assertEqual(EmailAddress.objects.all().count(), 1)
        #self.assertEqual(EmailAddress.objects.all_them().count(), 2)

        #we can now create that contact reusing a previous id
        #self.anotherAgainContactData = self.editingContactData.copy()
        #self.anotherAgainContactData['first_name'] = 'A new name'
        #del self.anotherAgainContactData['id']
        #self.anotherAgainContactData['emails'] = ["anewtestaddress@test.com"]
        #resp = self.api_client.post('/api/v1/contact/', format='json', data=self.anotherAgainContactData, authentication=self.get_credentials_other('yoko'))
        #self.assertEqual(Contact.objects.all().count(), 3)
        #self.assertEqual(EmailAddress.objects.all().count(), 2)
        #self.assertEqual(EmailAddress.objects.all_them().count(), 3)

        #and finally, if i change the email I can re-enable the contact
        #self.otherContactData['hidden'] = False
        #self.otherContactData['emails'] = ['ohell@test.com']
        #resp = self.api_client.put("/api/v1/contact/%s/" % self.otherContact.id, data=self.otherContactData, authentication=self.get_credentials_other('yoko'))
        #self.assertEqual(Contact.objects.all().count(), 3)
        #self.assertEqual(EmailAddress.objects.all().count(), 3)
        #self.assertEqual(EmailAddress.objects.all_them().count(), 4)
