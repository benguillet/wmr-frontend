from os.path import normpath, abspath, dirname, join
import os
import sys

app_path = normpath(join(dirname(abspath(__file__)), '..'))
sys.path.append(app_path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
