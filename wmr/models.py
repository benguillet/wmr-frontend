from django.db import models
from django.contrib.auth.models import User
from wmr.thriftapi.ttypes import JobRequest, State
from datetime import datetime
from django.conf import settings


class Dataset(models.Model):
    name = models.CharField("Dataset name", max_length=150, blank=True,
        help_text='A human-readable name')
    path = models.CharField("Cluster path", max_length=150,
        help_text='The path on the cluster (ex: "/data/foo", "s3://my-bucket/data")')
    owner = models.ForeignKey(User)
    public = models.BooleanField()
    upload_time = models.DateTimeField(null=True, default=datetime.now, editable=False)
    
    class Meta:
        ordering = ['-name', '-upload_time']
    
    def has_permission(self, user):
        return self.public == True or self.owner == user
    
    def __unicode__(self):
        if self.name != '':
            return self.name
        else:
            return self.path


LANGUAGES = getattr(settings, 'WMR_LANGUAGES', (
    ('python3', 'Python 3'),
    ('scheme-i', 'Scheme (Imperative)'),
    ('scheme-f', 'Scheme (Functional)'),
    ('cpp', 'C++'),
    ('java', 'Java'),
))

SORT_OPTIONS = (
    ('a', 'Alphabetic'),
    ('n', 'Numeric'),
)

if hasattr(settings, 'WMR_DEFAULT_LANGUAGE'):
    lang_kwargs = {'default': settings.WMR_DEFAULT_LANGUAGE}
else:
    lang_kwargs = {}

class Configuration(models.Model):
    name = models.CharField(max_length=50, blank=True)
    language = models.CharField(max_length=25, choices=LANGUAGES, **lang_kwargs)
    input = models.ForeignKey(Dataset)
    mapper = models.TextField()
    reducer = models.TextField()
    map_tasks = models.IntegerField(null=True, blank=True)
    reduce_tasks = models.IntegerField(null=True, blank=True)
    sort = models.CharField(max_length=1, choices=SORT_OPTIONS,
                            default=SORT_OPTIONS[0][0])
    
    owner = models.ForeignKey(User)
    creation_time = models.DateTimeField(default=datetime.now, editable=False)
    
    class Meta:
        ordering = ['-creation_time']
    
    def to_thrift_request(self, test=False):
        """Creates and returns Thrift JobRequest from this configuration."""
        numeric_sort = (self.sort == 'n')
        
        return JobRequest(
            name=self.name,
            user=self.owner.username,
            language=self.language,
            test=test,
            input=self.input.path,
            mapper=self.mapper,
            reducer=self.reducer,
            mapTasks=self.map_tasks,
            reduceTasks=self.reduce_tasks,
            numericSort=numeric_sort)
    
    def update_from_other(self, other):
        """Copies fields *except* owner from other."""
        self.name = other.name
        self.language = other.language
        self.input = other.input
        self.mapper = other.mapper
        self.reducer = other.reducer
        self.map_tasks = other.map_tasks
        self.reduce_tasks = other.reduce_tasks
    
    def __unicode__(self):
        if self.name != '':
            return self.name
        else:
            return '{0} {1}'.format(self.owner, self.creation_time)


class SavedConfiguration(Configuration):
    public = models.BooleanField()
    update_time = models.DateTimeField(default=datetime.now, editable=False)
    
    class Meta:
        ordering = ['-update_time']
    
    def touch(self):
        self.update_time = datetime.now()
    
    def has_permission(self, user):
        return self.public == True or self.owner == user
    
    def __unicode__(self):
        return self.name


COMPLETION_STATE_UNKNOWN = 0
COMPLETION_STATE_SUCCESSFUL = 3
COMPLETION_STATE_FAILED = 4
COMPLETION_STATE_KILLED = 5
COMPLETION_STATES = [
    (COMPLETION_STATE_UNKNOWN, 'Unknown/Not Complete'),
    (COMPLETION_STATE_SUCCESSFUL, 'Successful'),
    (COMPLETION_STATE_FAILED, 'Failed'),
    (COMPLETION_STATE_KILLED, 'Killed'),
]

class Job(models.Model):
    config = models.ForeignKey(Configuration)
    test = models.BooleanField()
    
    backend_id = models.IntegerField()
    hadoop_id = models.CharField(max_length=50, blank=True)
    completion_state = models.IntegerField(choices=COMPLETION_STATES,
                                           default=COMPLETION_STATE_UNKNOWN)
    
    owner = models.ForeignKey(User)
    submit_time = models.DateTimeField(default=datetime.now, editable=False)
    
    class Meta:
        ordering = ['-submit_time']
    
    def update_status(self, status):
        """
        Update this job's information from the Thrift JobStatus object provided.
        Returns self (to call save() afterward).
        """
        if status.state in (State.SUCCESSFUL, State.FAILED, State.KILLED):
            if status.state == State.SUCCESSFUL:
                self.completion_state = COMPLETION_STATE_SUCCESSFUL
            elif status.state == State.FAILED:
                self.completion_state = COMPLETION_STATE_FAILED
            elif status.state == State.KILLED:
                self.completion_state = COMPLETION_STATE_KILLED
        if status.info and status.info.nativeID:
            self.hadoop_id = status.info.nativeID
        return self
    
    def __unicode__(self):
        return unicode(self.config)
