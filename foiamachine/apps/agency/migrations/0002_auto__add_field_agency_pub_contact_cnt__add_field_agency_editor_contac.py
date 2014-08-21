# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Agency.pub_contact_cnt'
        db.add_column('agency_agency', 'pub_contact_cnt',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Agency.editor_contact_cnt'
        db.add_column('agency_agency', 'editor_contact_cnt',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Agency.pub_contact_cnt'
        db.delete_column('agency_agency', 'pub_contact_cnt')

        # Deleting field 'Agency.editor_contact_cnt'
        db.delete_column('agency_agency', 'editor_contact_cnt')


    models = {
        'agency.agency': {
            'Meta': {'object_name': 'Agency'},
            'contacts': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'agency_related_contacts'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['contacts.Contact']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'deprecated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'editor_contact_cnt': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'government': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['government.Government']"}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'nay_votes': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'pub_contact_cnt': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
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

    complete_apps = ['agency']