from django.contrib import admin
from wmr.models import Dataset, SavedConfiguration
from registration.models import RegistrationKey
from django.contrib.sites.models import Site


admin.site.register(Dataset)
admin.site.register(SavedConfiguration)
admin.site.register(RegistrationKey)

admin.site.unregister(Site)
