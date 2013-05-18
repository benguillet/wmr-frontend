# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Dataset'
        db.create_table('wmr_dataset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150, blank=True)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('upload_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, null=True)),
        ))
        db.send_create_signal('wmr', ['Dataset'])

        # Adding model 'Configuration'
        db.create_table('wmr_configuration', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('input', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wmr.Dataset'])),
            ('mapper', self.gf('django.db.models.fields.TextField')()),
            ('reducer', self.gf('django.db.models.fields.TextField')()),
            ('map_tasks', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('reduce_tasks', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('sort', self.gf('django.db.models.fields.CharField')(default='a', max_length=1)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('creation_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('wmr', ['Configuration'])

        # Adding model 'SavedConfiguration'
        db.create_table('wmr_savedconfiguration', (
            ('configuration_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['wmr.Configuration'], unique=True, primary_key=True)),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('update_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('wmr', ['SavedConfiguration'])

        # Adding model 'Job'
        db.create_table('wmr_job', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('config', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wmr.Configuration'])),
            ('test', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('backend_id', self.gf('django.db.models.fields.IntegerField')()),
            ('hadoop_id', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('completion_state', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('submit_time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('wmr', ['Job'])


    def backwards(self, orm):
        
        # Deleting model 'Dataset'
        db.delete_table('wmr_dataset')

        # Deleting model 'Configuration'
        db.delete_table('wmr_configuration')

        # Deleting model 'SavedConfiguration'
        db.delete_table('wmr_savedconfiguration')

        # Deleting model 'Job'
        db.delete_table('wmr_job')


    models = {
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
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'wmr.configuration': {
            'Meta': {'ordering': "['-creation_time']", 'object_name': 'Configuration'},
            'creation_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'input': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wmr.Dataset']"}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'map_tasks': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'mapper': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'reduce_tasks': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'reducer': ('django.db.models.fields.TextField', [], {}),
            'sort': ('django.db.models.fields.CharField', [], {'default': "'a'", 'max_length': '1'})
        },
        'wmr.dataset': {
            'Meta': {'ordering': "['-upload_time']", 'object_name': 'Dataset'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'upload_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'null': 'True'})
        },
        'wmr.job': {
            'Meta': {'ordering': "['-submit_time']", 'object_name': 'Job'},
            'backend_id': ('django.db.models.fields.IntegerField', [], {}),
            'completion_state': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'config': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wmr.Configuration']"}),
            'hadoop_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'submit_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'test': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'wmr.savedconfiguration': {
            'Meta': {'ordering': "['-update_time']", 'object_name': 'SavedConfiguration', '_ormbases': ['wmr.Configuration']},
            'configuration_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['wmr.Configuration']", 'unique': 'True', 'primary_key': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'update_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        }
    }

    complete_apps = ['wmr']
