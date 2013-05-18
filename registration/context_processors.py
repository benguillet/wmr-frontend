from django.conf import settings

REGISTRATION_ENABLED = getattr(settings, 'REGISTRATION_ENABLED', False)

def registration_enabled(request):
    return {'registration_enabled': REGISTRATION_ENABLED}