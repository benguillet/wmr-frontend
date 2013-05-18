from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.conf import settings
from os import path

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# Get admin path (based on path module is loaded from)
ADMIN_MEDIA_ROOT = path.normpath(path.join(path.dirname(admin.__file__), 'media'))

urlpatterns = patterns('',
    (r'^$', 'django.views.generic.simple.redirect_to', {'url': 'jobs/new'}),
    
    # WMR
    (r'^datasets/$', 'wmr.views.dataset_list'),
    (r'^datasets/new/$', 'wmr.views.dataset_new'),
    (r'^datasets/(?P<dataset_id>\d+)/delete/$', 'wmr.views.dataset_delete'),
    (r'^jobs/$', 'wmr.views.job_list'),
    (r'^jobs/new/$', 'wmr.views.job_new'),
    (r'^jobs/(?P<job_id>\d+)/kill/$', 'wmr.views.job_kill'),
    (r'^jobs/(?P<job_id>\d+)/$', 'wmr.views.job_view'),
    (r'^configs/$', 'wmr.views.configs'),
    
    # Admin
    (r'^admin/', include(admin.site.urls)),
    
    # Media
    (r'^media/admin/(?P<path>.*)', 'django.views.static.serve',
        {'document_root': ADMIN_MEDIA_ROOT}),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),
    
    # Login/logout
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
    (r'^accounts/changepassword/$', 'django.contrib.auth.views.password_change'),
    (r'^accounts/passwordchanged/$', 'django.contrib.auth.views.password_change_done')
)

#Password reset requires an email server to be setup, which I think is a reasonable thing, but am not setting up for this realease.
#urlpatterns += patterns('',
#    (r'^accounts/resetpassword/$', 'django.contrib.auth.views.password_reset'),
#    (r'^accounts/passwordreset/$', 'django.contrib.auth.views.password_reset_done'),
#    (r'^accounts/confirmpassword/(?P<uidb36>\w+)/(?P<token>.*)/$', 'django.contrib.auth.views.password_reset_confirm'),
#    (r'^accounts/passwordconfirmed/$', 'django.contrib.auth.views.password_reset_complete'),
#)

if getattr(settings, 'REGISTRATION_ENABLED', False):
    # Registration
    urlpatterns += patterns('registration.views',
        (r'^accounts/register/$', 'create_account'),
        (r'^accounts/register/thanks/$', 'create_account_done'),
    )
