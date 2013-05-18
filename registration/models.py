from django.db import models 
from datetime import datetime, timedelta
from django.conf import settings

class RegistrationKey(models.Model):
    name = models.CharField(max_length=150, blank=True, 
	    help_text='The keyword that a user enters when they register an account.')

    # Currently return 24 hours after the current time
    def default_expiration():
	return datetime.now() + timedelta(days=1)

    expiration_time = models.DateTimeField(null=True, default=default_expiration())

    class Meta:
        ordering = ['-expiration_time']

    def __unicode__(self):
	return self.name

    def is_expired(self):
	return self.expiration_time < datetime.now()
