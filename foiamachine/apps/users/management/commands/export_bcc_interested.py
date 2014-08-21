from django.core.management.base import BaseCommand
from apps.users.models import InterestedParty

class Command(BaseCommand):

    def handle(self, *args, **options):
    	f = open('bcc_interested_export.txt', 'wb')
        parties = InterestedParty.objects.all()
        emails = map(lambda x: x.email, parties)
        export_str = ''
        export_str += ','.join(emails)
        print len(emails)
        f.write(export_str)

