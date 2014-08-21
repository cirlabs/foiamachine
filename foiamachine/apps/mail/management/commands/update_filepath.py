from apps.mail.attachment import *
from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache

from datetime import datetime
from django.conf import settings
from django.db import connection
from django.db import transaction


class Command(BaseCommand):
    settings.USE_SE = True
    transaction.commit_manually()
    cursor = connection.cursor()
    for attachment in Attachment.objects.filter(created__lte=datetime(2014, 05, 17)):
        result = cursor.execute("SELECT file FROM mail_attachment WHERE id = %s", [attachment.id])
        row = cursor.fetchone()
        filename = "media/"+row[0]
        query = "update mail_attachment SET file='%s' where id=%s;" % (filename, attachment.id)
        print query
        result = cursor.execute(query)
        cursor.execute("COMMIT;")
        #transaction.commit()
        #attachment.update(file=filename)
