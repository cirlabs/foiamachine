from apps.core.user_test_base import UserTestBase
from apps.requests.models import Request
from apps.agency.models import Agency
from apps.contacts.models import Contact
from datetime import datetime
from django.utils import timezone
import json
import pytz

class RequestSending(UserTestBase):
    '''
    Permission settings are tested in the users app
    '''
    def test_send_request(self):
        self.create_request('yoko')
        self.assertEqual(Request.objects.all().count(), 1)
        self.assertEqual(self.request.can_send, False)
        self.create_agency()
        contactData = {
            'first_name': "FOIA",
            "last_name": "MACHINE",
            "dob": "1901-07-19",
            "notes": ["The official FOIA Machine contact, it has no phone"],
            "phone_numbers": ["999-999-9999"],
            "titles": ["Public Information Machine"],
            "emails": ["info@foiamachine.org"],
            "addresses": ["New York, New York"],
            "agencyId": self.agency.id
        }
        self.create_contact(contactData)
        self.assertEqual(Agency.objects.all().count(), 1)
        self.assertEqual(Contact.objects.all().count(), 1)
        self.request.title = "A new test title"
        self.request.government = self.agency.government
        self.request.agency = self.agency
        self.request.contacts = [self.contact]
        self.request.save()
        self.assertEqual(self.request.can_send, True)
        self.assertEqual(self.request.sent, False)
        self.request.send()
        self.assertEqual(self.request.can_send, False)
        self.assertEqual(self.request.sent, True)
        #have to override a bit to test the due dates, no one likes a request before xmas
        #also, beware, if Government.get_holiday_dates changes this could change!
        est = pytz.timezone('US/Eastern')
        self.request.scheduled_send_date = est.localize(datetime(2013, 12, 23))
        self.request.due_date = None
        self.request.save()
        self.assertEqual(self.request.get_due_date, est.localize(datetime(2014, 1, 23)))
