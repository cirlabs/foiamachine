from django.db import models

import boto
import django
import mimetypes
import datetime
from django.conf import settings

# Avoid circular references with Request, which needs to store attachments
# for initial send
def content_file_name(instance, filename):
    #return '%s/%s/%s' % ('attachments', instance.user.username,filename)
    return '%s/%s/%s/_%s_%s' % (settings.DEFAULT_S3_PATH, 'attachments', instance.user.username,datetime.datetime.now(), filename)

class Attachment(models.Model):
    from django.contrib.auth.models import User
    user = models.ForeignKey(User)
    file = models.FileField(upload_to=content_file_name, max_length=255)
    created = models.DateTimeField(auto_now_add=True)

    def get_mimetype(self):
        format, enc = mimetypes.guess_type(self.get_filename())
        return format

    def get_messages(self):
        return self.message_attachments.all()

    @property
    def get_filename(self):
        fname = self.file.name.split('/')[-1]
        if fname.startswith('_'):
            return fname.split('_', 2)[2]
        return fname

    @property
    def get_public_url(self):
        return self.file.url

    @property
    def url(self):
        return self.file.url.split("?")[0]

    @property
    def get_key(self):
        return "%s" % (self.file.name)

    def save(self, *args, **kwargs):
        super(Attachment, self).save(*args, **kwargs)
        if settings.USE_S3:
            conn = boto.s3.connection.S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
            bucket = conn.create_bucket(settings.AWS_STORAGE_BUCKET_NAME)
            k = boto.s3.key.Key(bucket)
            k.key = self.get_key
            k.set_acl('private')
