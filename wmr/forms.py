from django import forms
from django.utils.html import mark_safe
from wmr.models import Configuration, Dataset
from itertools import chain


class ConfigurationForm(forms.ModelForm):
    #required_css_class="required-field"
    error_css_class="error-field"
    
    class Meta:
        model = Configuration
        exclude = ['owner', '''input''']
    
    class Media:
        js = ('form.js',)
    
    input_choices = {
        'dataset': 'input',
        'path': 'input_path',
        'upload': 'input_file',
        'input': 'input_text',
    }
    mapper_choices = {
        'upload': 'mapper_file',
        'input': 'mapper',
    }
    reducer_choices = {
        'upload': 'reducer_file',
        'input': 'reducer',
    }
    input_path = forms.CharField(required=False, label='Cluster Path')
    input_text = forms.CharField(required=False, label='Direct Input',
                                 widget=forms.widgets.Textarea)
    input_file = forms.FileField(required=False, label='Upload')
    mapper_file = forms.FileField(required=False, label='Upload')
    reducer_file = forms.FileField(required=False, label='Upload')
    
    # Override model defaults
    input = forms.ModelChoiceField(Dataset.objects.filter(public=True), required=False,
                                   label='Cluster Dataset')
    mapper = forms.CharField(required=False, label='Direct Input',
                             widget=forms.widgets.Textarea)
    reducer = forms.CharField(required=False, label='Direct Input',
                              widget=forms.widgets.Textarea)
    
    def __init__(self, *args, **kwargs):
        super(ConfigurationForm, self).__init__(*args, **kwargs)
        
        self.input_source = RadioGroup(self, 'input_source',
            self.input_choices, initial='path')
        self.mapper_source = RadioGroup(self, 'mapper_source',
            self.mapper_choices, initial='input')
        self.reducer_source = RadioGroup(self, 'reducer_source',
            self.reducer_choices, initial='input')
    
    def _require_field(self, cleaned_data, field):
        if not cleaned_data.get(field):
            self._errors[field] = self.error_class(
                [self.fields[field].error_messages['required']])
            del cleaned_data[field]
    
    def clean(self):
        cleaned_data = super(ConfigurationForm, self).clean()
        
        # Validate radio groups
        for radio_group_name in ('input_source', 'mapper_source', 'reducer_source'):
            radio_group = getattr(self, radio_group_name)
            try:
                data = self.data[radio_group_name]
                radio_group_value = radio_group.clean(data)
                cleaned_data[radio_group_name] = radio_group_value
                
                # Require selected field
                if radio_group_value:
                    source_field = radio_group.choices[radio_group_value]
                    self._require_field(cleaned_data, source_field)
            
            except forms.ValidationError as ex:
                self._errors[radio_group_name] = self.error_class(ex.messages)
                if radio_group_name in cleaned_data:
                    del cleaned_data[radio_group_name]
        
        return cleaned_data


class PublicDatasetForm(forms.ModelForm):
    class Meta:
        model = Dataset
        fields = ('name', 'path')


class RadioGroup(object):
    default_error_messages = {
        'invalid_choice': u'%(value)s is not a valid choice.',
        'required': u'Please make a choice.',
    }
    
    def __init__(self, form, name, choices, initial=None, required=True):
        self.form = form
        self.name = name
        self.choices = choices
        self.error_messages = self.default_error_messages
        self.initial = initial
        self.required = required
        
        self.items = dict((value, RadioButton(self, value)) for value in choices)
    
    def __getitem__(self, name):
        return self.items[name]
    
    def get_value(self):
        # Handle this specially so that the value can be reassigned by the
        # form's clean() method
        if self.form.is_bound:
            return self.form.data.get(self.name, self.initial)
        else:
            return self.form.initial.get(self.name, self.initial)
    
    def clean(self, value):
        if not value:
            if self.required:
                raise forms.ValidationError(self.error_messages['required'])
            else:
                return None
        elif value not in self.items:
            raise forms.ValidationError(self.error_messages['invalid_choice'] %
                                        {'value': value})
        return value
    
    @property
    def errors(self):
        try:
            return self.form._errors[self.name]
        except KeyError:
            return None


class RadioButton(object):
    def __init__(self, group, value):
        self.group = group
        self.value = value
    
    def __unicode__(self):
        out = (u'<input type="radio" name="{name}" value="{value}" '
               u'id="{prefix}{name}_{value}" ').format(
               name=self.group.name, value=self.value, prefix='id_')
        if self.group.get_value() == self.value:
            out += u'checked="checked" '
        out += u'/>'
        return mark_safe(out)
