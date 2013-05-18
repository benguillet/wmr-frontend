from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from registration.forms import RegistrationForm

def create_account(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            
            user = User.objects.create_user(
                form.cleaned_data['email'],
                form.cleaned_data['email'],
                form.cleaned_data['password'],
            )
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            
            # Log in the new user. Note that Django requires that we call
            # authenticate() despite its apparent redundancy in this case
            user = authenticate(username=user.username, password=form.cleaned_data['password'])
            login(request, user)
            
            return redirect(reverse('registration.views.create_account_done'))
    else:
        form = RegistrationForm()
    
    return render_to_response('registration/create_account.html', RequestContext(request, {
        'form': form,
    }))


@login_required
def create_account_done(request):
    return render_to_response('registration/thanks.html', RequestContext(request), {})