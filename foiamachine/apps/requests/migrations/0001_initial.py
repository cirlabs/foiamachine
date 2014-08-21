# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ResponseFormat'
        db.create_table('requests_responseformat', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django_extensions.db.fields.AutoSlugField')(allow_duplicates=False, max_length=50, separator=u'-', blank=True, populate_from=('name',), overwrite=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('file_extension', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
        ))
        db.send_create_signal('requests', ['ResponseFormat'])

        # Adding model 'RecordType'
        db.create_table('requests_recordtype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django_extensions.db.fields.AutoSlugField')(allow_duplicates=False, max_length=50, separator=u'-', blank=True, populate_from=('name',), overwrite=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('requests', ['RecordType'])

        # Adding model 'Request'
        db.create_table('requests_request', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('government', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['government.Government'], null=True, blank=True)),
            ('agency', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['agency.Agency'], null=True, blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('free_edit_body', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('printed', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='printed_request', null=True, to=orm['mail.Attachment'])),
            ('private', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('slug', self.gf('django_extensions.db.fields.AutoSlugField')(allow_duplicates=False, max_length=50, separator=u'-', blank=True, populate_from=('title',), overwrite=False)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('date_fulfilled', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('due_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('scheduled_send_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('request_start_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('request_end_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('keep_private', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('fee_waiver', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('phone_contact', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('prefer_electornic', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('max_cost', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('thread_lookup', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('last_contact_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('first_response_time', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('lifetime', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('days_outstanding', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('response_overdue', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('official_stats', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('requests', ['Request'])

        # Adding M2M table for field documents on 'Request'
        db.create_table('requests_request_documents', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('request', models.ForeignKey(orm['requests.request'], null=False)),
            ('document', models.ForeignKey(orm['doccloud.document'], null=False))
        ))
        db.create_unique('requests_request_documents', ['request_id', 'document_id'])

        # Adding M2M table for field contacts on 'Request'
        db.create_table('requests_request_contacts', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('request', models.ForeignKey(orm['requests.request'], null=False)),
            ('contact', models.ForeignKey(orm['contacts.contact'], null=False))
        ))
        db.create_unique('requests_request_contacts', ['request_id', 'contact_id'])

        # Adding M2M table for field attachments on 'Request'
        db.create_table('requests_request_attachments', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('request', models.ForeignKey(orm['requests.request'], null=False)),
            ('attachment', models.ForeignKey(orm['mail.attachment'], null=False))
        ))
        db.create_unique('requests_request_attachments', ['request_id', 'attachment_id'])

        # Adding M2M table for field supporters on 'Request'
        db.create_table('requests_request_supporters', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('request', models.ForeignKey(orm['requests.request'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('requests_request_supporters', ['request_id', 'user_id'])

        # Adding M2M table for field record_types on 'Request'
        db.create_table('requests_request_record_types', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('request', models.ForeignKey(orm['requests.request'], null=False)),
            ('recordtype', models.ForeignKey(orm['requests.recordtype'], null=False))
        ))
        db.create_unique('requests_request_record_types', ['request_id', 'recordtype_id'])

        # Adding M2M table for field acceptable_responses on 'Request'
        db.create_table('requests_request_acceptable_responses', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('request', models.ForeignKey(orm['requests.request'], null=False)),
            ('responseformat', models.ForeignKey(orm['requests.responseformat'], null=False))
        ))
        db.create_unique('requests_request_acceptable_responses', ['request_id', 'responseformat_id'])

        # Adding model 'ViewableLink'
        db.create_table('requests_viewablelink', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('request', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['requests.Request'], null=True, blank=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('requests', ['ViewableLink'])

        # Adding model 'Notification'
        db.create_table('requests_notification', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.IntegerField')()),
            ('sent', self.gf('django.db.models.fields.DateField')(auto_now_add=True, null=True, blank=True)),
            ('request', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['requests.Request'], null=True, blank=True)),
        ))
        db.send_create_signal('requests', ['Notification'])

        # Adding model 'Organization'
        db.create_table('requests_organization', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('state', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('postal_code', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('requests', ['Organization'])

        # Adding model 'Event'
        db.create_table('requests_event', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('request', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['requests.Request'])),
            ('type', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('requests', ['Event'])


    def backwards(self, orm):
        # Deleting model 'ResponseFormat'
        db.delete_table('requests_responseformat')

        # Deleting model 'RecordType'
        db.delete_table('requests_recordtype')

        # Deleting model 'Request'
        db.delete_table('requests_request')

        # Removing M2M table for field documents on 'Request'
        db.delete_table('requests_request_documents')

        # Removing M2M table for field contacts on 'Request'
        db.delete_table('requests_request_contacts')

        # Removing M2M table for field attachments on 'Request'
        db.delete_table('requests_request_attachments')

        # Removing M2M table for field supporters on 'Request'
        db.delete_table('requests_request_supporters')

        # Removing M2M table for field record_types on 'Request'
        db.delete_table('requests_request_record_types')

        # Removing M2M table for field acceptable_responses on 'Request'
        db.delete_table('requests_request_acceptable_responses')

        # Deleting model 'ViewableLink'
        db.delete_table('requests_viewablelink')

        # Deleting model 'Notification'
        db.delete_table('requests_notification')

        # Deleting model 'Organization'
        db.delete_table('requests_organization')

        # Deleting model 'Event'
        db.delete_table('requests_event')


    models = {
        'agency.agency': {
            'Meta': {'object_name': 'Agency'},
            'contacts': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'agency_related_contacts'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['contacts.Contact']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'deprecated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'government': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['government.Government']"}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'nay_votes': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'slug': ('django_extensions.db.fields.AutoSlugField', [], {'allow_duplicates': 'False', 'max_length': '50', 'separator': "u'-'", 'blank': 'True', 'populate_from': "('name',)", 'overwrite': 'False'}),
            'yay_votes': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contacts.address': {
            'Meta': {'object_name': 'Address'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deprecated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nay_votes': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'yay_votes': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
        },
        'contacts.contact': {
            'Meta': {'object_name': 'Contact'},
            'addresses': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['contacts.Address']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'deprecated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'dob': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'emails': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['core.EmailAddress']", 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'middle_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'nay_votes': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'notes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['contacts.Note']", 'null': 'True', 'blank': 'True'}),
            'phone_numbers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['contacts.Phone']", 'null': 'True', 'blank': 'True'}),
            'titles': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['contacts.Title']", 'null': 'True', 'blank': 'True'}),
            'yay_votes': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
        },
        'contacts.note': {
            'Meta': {'object_name': 'Note'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deprecated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nay_votes': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'yay_votes': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
        },
        'contacts.phone': {
            'Meta': {'object_name': 'Phone'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deprecated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nay_votes': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'yay_votes': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
        },
        'contacts.title': {
            'Meta': {'object_name': 'Title'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deprecated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nay_votes': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'yay_votes': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.emailaddress': {
            'Meta': {'object_name': 'EmailAddress'},
            'content': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deprecated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nay_votes': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'yay_votes': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
        },
        'doccloud.document': {
            'Meta': {'ordering': "['created_at']", 'object_name': 'Document'},
            'access_level': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True', 'blank': 'True'}),
            'dc_properties': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['doccloud.DocumentCloudProperties']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django_extensions.db.fields.AutoSlugField', [], {'allow_duplicates': 'False', 'max_length': '50', 'separator': "u'-'", 'blank': 'True', 'populate_from': "('title',)", 'overwrite': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'doccloud.documentcloudproperties': {
            'Meta': {'object_name': 'DocumentCloudProperties'},
            'dc_id': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'dc_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'government.adminname': {
            'Meta': {'object_name': 'AdminName'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deprecated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name_plural': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'nay_votes': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'yay_votes': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
        },
        'government.feeexemptionother': {
            'Meta': {'object_name': 'FeeExemptionOther'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deprecated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'nay_votes': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'slug': ('django_extensions.db.fields.AutoSlugField', [], {'allow_duplicates': 'False', 'max_length': '50', 'separator': "u'-'", 'blank': 'True', 'populate_from': "('name',)", 'overwrite': 'False'}),
            'source': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'typee': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'yay_votes': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
        },
        'government.government': {
            'Meta': {'object_name': 'Government'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deprecated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'holidays': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['government.Holiday']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'nation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['government.Nation']", 'null': 'True', 'blank': 'True'}),
            'nay_votes': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'slug': ('django_extensions.db.fields.AutoSlugField', [], {'allow_duplicates': 'False', 'max_length': '50', 'separator': "u'-'", 'blank': 'True', 'populate_from': "('name',)", 'overwrite': 'False'}),
            'statutes': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'related_statutes'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['government.Statute']"}),
            'yay_votes': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
        },
        'government.holiday': {
            'Meta': {'object_name': 'Holiday'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'deprecated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'nay_votes': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'yay_votes': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
        },
        'government.language': {
            'Meta': {'object_name': 'Language'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deprecated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'nay_votes': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'slug': ('django_extensions.db.fields.AutoSlugField', [], {'allow_duplicates': 'False', 'max_length': '50', 'separator': "u'-'", 'blank': 'True', 'populate_from': "('name',)", 'overwrite': 'False'}),
            'yay_votes': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
        },
        'government.nation': {
            'Meta': {'object_name': 'Nation'},
            'admin_0_name': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'admin_0_nations'", 'null': 'True', 'to': "orm['government.AdminName']"}),
            'admin_1_name': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'admin_1_nations'", 'null': 'True', 'to': "orm['government.AdminName']"}),
            'admin_2_name': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'admin_2_nations'", 'null': 'True', 'to': "orm['government.AdminName']"}),
            'admin_3_name': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'admin_3_nations'", 'null': 'True', 'to': "orm['government.AdminName']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deprecated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'foi_languages': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['government.Language']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'nay_votes': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'primary_language': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'primary_language_nations'", 'null': 'True', 'to': "orm['government.Language']"}),
            'slug': ('django_extensions.db.fields.AutoSlugField', [], {'allow_duplicates': 'False', 'max_length': '50', 'separator': "u'-'", 'blank': 'True', 'populate_from': "('name',)", 'overwrite': 'False'}),
            'yay_votes': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
        },
        'government.statute': {
            'Meta': {'object_name': 'Statute'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'days_till_due': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'deprecated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'designator': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'fees_exemptions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['government.FeeExemptionOther']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nay_votes': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'short_title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django_extensions.db.fields.AutoSlugField', [], {'allow_duplicates': 'False', 'max_length': '50', 'separator': "u'-'", 'blank': 'True', 'populate_from': "('short_title',)", 'overwrite': 'False'}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'updates': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['government.Update']", 'null': 'True', 'blank': 'True'}),
            'yay_votes': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
        },
        'government.update': {
            'Meta': {'object_name': 'Update'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deprecated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'headline': ('django.db.models.fields.CharField', [], {'default': "'The latest'", 'max_length': '1024'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nay_votes': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'pubbed': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'yay_votes': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
        },
        'mail.attachment': {
            'Meta': {'object_name': 'Attachment'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'requests.event': {
            'Meta': {'object_name': 'Event'},
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'request': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['requests.Request']"}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        },
        'requests.notification': {
            'Meta': {'object_name': 'Notification'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'request': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['requests.Request']", 'null': 'True', 'blank': 'True'}),
            'sent': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        },
        'requests.organization': {
            'Meta': {'object_name': 'Organization'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'state': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'requests.recordtype': {
            'Meta': {'object_name': 'RecordType'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django_extensions.db.fields.AutoSlugField', [], {'allow_duplicates': 'False', 'max_length': '50', 'separator': "u'-'", 'blank': 'True', 'populate_from': "('name',)", 'overwrite': 'True'})
        },
        'requests.request': {
            'Meta': {'object_name': 'Request'},
            'acceptable_responses': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['requests.ResponseFormat']", 'null': 'True', 'blank': 'True'}),
            'agency': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['agency.Agency']", 'null': 'True', 'blank': 'True'}),
            'attachments': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['mail.Attachment']", 'null': 'True', 'blank': 'True'}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'contacts': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'related_contacts'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['contacts.Contact']"}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_fulfilled': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'date_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'days_outstanding': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'related_docs'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['doccloud.Document']"}),
            'due_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'fee_waiver': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'first_response_time': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'free_edit_body': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'government': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['government.Government']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keep_private': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_contact_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'lifetime': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'max_cost': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'official_stats': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'phone_contact': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'prefer_electornic': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'printed': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'printed_request'", 'null': 'True', 'to': "orm['mail.Attachment']"}),
            'private': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'record_types': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['requests.RecordType']", 'null': 'True', 'blank': 'True'}),
            'request_end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'request_start_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'response_overdue': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'scheduled_send_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django_extensions.db.fields.AutoSlugField', [], {'allow_duplicates': 'False', 'max_length': '50', 'separator': "u'-'", 'blank': 'True', 'populate_from': "('title',)", 'overwrite': 'False'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'supporters': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'supporter'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'thread_lookup': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'requests.responseformat': {
            'Meta': {'object_name': 'ResponseFormat'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'file_extension': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django_extensions.db.fields.AutoSlugField', [], {'allow_duplicates': 'False', 'max_length': '50', 'separator': "u'-'", 'blank': 'True', 'populate_from': "('name',)", 'overwrite': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        },
        'requests.viewablelink': {
            'Meta': {'object_name': 'ViewableLink'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'request': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['requests.Request']", 'null': 'True', 'blank': 'True'})
        },
        'taggit.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        'taggit.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taggit_taggeditem_tagged_items'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taggit_taggeditem_items'", 'to': "orm['taggit.Tag']"})
        }
    }

    complete_apps = ['requests']