from django.core.management.base import BaseCommand
from apps.contacts.models import *
from apps.agency.models import *
from apps.core.models import *
from apps.doccloud.models import *
from apps.government.models import *
from apps.mail.models import *
from apps.requests.models import *



class Command(BaseCommand):

    def handle(self, *args, **options):
        Agency.objects.all().delete()
        Title.objects.all().delete()
        Phone.objects.all().delete()
        Address.objects.all().delete()
        Note.objects.all().delete()
        Contact.objects.all().delete()
        #BaseData.objects.all().delete()
        EmailAddress.objects.all().delete()
        DocumentCloudProperties.objects.all().delete()
        Document.objects.all().delete()
        Language.objects.all().delete()
        AdminName.objects.all().delete()
        Nation.objects.all().delete()
        Statute.objects.all().delete()
        Government.objects.all().delete()
        Attachment.objects.all().delete()
        MessageId.objects.all().delete()
        MailMessage.objects.all().delete()
        #MailBox.objects.all().delete()
        ResponseFormat.objects.all().delete()
        RecordType.objects.all().delete()
        Request.objects.all().delete()
        Organization.objects.all().delete()
        Event.objects.all().delete()