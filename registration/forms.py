from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from registration.models import RegistrationKey
from django.conf import settings
from datetime import datetime

class RegistrationForm(forms.Form):
    error_css_class="error-field"
    required_css_class="required-field"
    
    email = forms.EmailField(label='Email', help_text='This will be your username.')
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    password = forms.CharField(widget=forms.widgets.PasswordInput)
    password_confirm = forms.CharField(widget=forms.widgets.PasswordInput,
                                       label='Confirm Password')
    
    # Automatically cleans the field (email) which is its suffix
    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            User.objects.get(username=email)
        except User.DoesNotExist:
            # Normal case
            return email
        else:
            raise ValidationError('Email is already registered.')


    # If enabled, set up timed registration keys
    if getattr(settings, 'REQUIRE_REGISTRATION_KEY', True):

        key = forms.CharField(widget=forms.widgets.PasswordInput,
                          label='Registration Key')
    
        def clean_key(self):
            key = self.cleaned_data['key']
            try:
                key = RegistrationKey.objects.get(name=key)
                if key.is_expired():
			raise ValidationError(
				'The registration key you entered is invalid.')
            except RegistrationKey.DoesNotExist:
                raise ValidationError('The registration key you entered is invalid')
            else:
                return key
    
    
    def clean(self):
        cleaned_data = self.cleaned_data
        
        if cleaned_data['password'] != cleaned_data['password_confirm']:
            self._errors['password'] = self.error_class(['Passwords did not match.'])
            del cleaned_data['password']
            del cleaned_data['password_confirm']
        
        return cleaned_data
