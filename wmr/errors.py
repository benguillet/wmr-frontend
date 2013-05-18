from django.utils.html import escape
from django.utils.safestring import mark_safe
from wmr.thriftapi.ttypes import *


class WMRError(object):
    class AdditionalInfo(object):
        def __init__(self, info):
            self.info = info
        
        def as_table(self):
            output = ''
            for key, value in self.info:
                title, content = self._html_for_pair(key, value)
                output += '<tr><th>{title}</th><td>{content}</td>'.format(
                            title=title, content=content)
            return mark_safe(output)
        
        def _html_for_pair(self, key, value):
            if key == 'exceptionType':
                return ('Type', escape(value))
            if key == 'exceptionMessage':
                return ('Message', escape(value))
            if key == 'stackTrace':
                return ('Stack Trace', '<pre>{0}</pre>'.format(escape(value)))
            if key == 'value':
                return ('Value', escape(value))
            if key == 'exitCode':
                return ('Exit Code', escape(value))
            if key == 'output':
                return ('Output', escape(value))
            if key == 'attempts':
                return ('Jobs Allowed', escape(value))
            if key == 'duration':
                return ('In Period',  '{0} minutes'.format(escape(value)))
            if key == 'cause':
                return ('Caused By',
                        '<pre>{0}: {1}\n{2}</pre>'.format(
                          escape(value['type']),
                          escape(value['message']),
                          escape(value['stackTrace'])))
        
        def __nonzero__(self):
            return bool(self.info)
            
    
    def __init__(self, ex, title=None, message=None, additional_info=None):
        self.ex = ex
        self.is_internal = False
        
        if message:
            self.message = message
        else:
            self.message = ex.message
        
        default_info = []
        if isinstance(ex, ValidationException):
            default_title = 'Validation Error'
            default_info = [('value', ex.value)]
        elif isinstance(ex, NotFoundException):
            default_title = 'Not Found'
        elif isinstance(ex, CompilationException):
            default_title = 'Compiler Error'
            default_info = [('exitCode', ex.code),
                            ('output', ex.output)]
        elif isinstance(ex, PermissionException):
            default_title = 'Permission Denied'
        elif isinstance(ex, IllegalJobStateException):
            default_title = 'Invalid Job State'
        elif isinstance(ex, QuotaException):
            default_title = 'Quota Exceeded'
            default_info = [('attempts', ex.attempts),
                            ('duration', ex.duration)]
        elif isinstance(ex, ForbiddenTestJobException):
            default_title = 'Test Jobs fobidden.'
        
        if title:
            self.title = title
        else:
            self.title = default_title
        
        if additional_info is None:
            additional_info = []
        self.additional_info = WMRError.AdditionalInfo(
            additional_info + default_info)

class WMRInternalError(WMRError):
    DEFAULT_TITLE = 'Internal Error'
    DEFAULT_MESSAGE = 'A serious error occurred in the WebMapReduce system. Please contact an administrator.'
    
    def __init__(self, ex, title=None, message=None, additional_info=None):
        self.ex = ex
        self.is_internal = True
        
        if title:
            self.title = title
        else:
            self.title = WMRInternalError.DEFAULT_TITLE
        
        if message:
            self.message = message
        else:
            self.message = WMRInternalError.DEFAULT_MESSAGE
        
        if additional_info:
            self.additional_info = WMRError.AdditionalInfo(additional_info)


class WMRBackendInternalError(WMRInternalError):
    def __init__(self, ex, title=None, message=None, additional_info=None):
        default_info = [
            ('exceptionMessage', ex.message),
        ]
        for cause in ex.causes:
            default_info.append(('cause', {
                'type': cause.type,
                'message': cause.message,
                'stackTrace': cause.stackTrace,
            }))
        
        if additional_info is None:
            additional_info = []
        
        WMRInternalError.__init__(self, ex, title, message,
                                  additional_info + default_info)


class WMRThriftError(WMRInternalError):
    def __init__(self, ex, title=None, message=None, additional_info=None):
        default_info = [
            ('exceptionMessage', str(ex)),
            ('exceptionType', type(ex).__name__)
        ]
        
        if additional_info is None:
            additional_info = []
        
        WMRInternalError.__init__(self, ex, title, message,
                                  additional_info + default_info)
