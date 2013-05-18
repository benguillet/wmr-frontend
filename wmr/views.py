from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required
from wmr.models import Job, Dataset, Configuration, SavedConfiguration
from wmr.forms import ConfigurationForm, PublicDatasetForm
from wmr.errors import WMRError, WMRBackendInternalError, WMRThriftError
from wmr import client
from wmr.thriftapi.ttypes import *
import datetime

@login_required
def job_new(request):
    error = flash = None
    if request.method == 'POST':
        form = ConfigurationForm(request.POST, request.FILES)
        if form.is_valid():
            # Handle input
            input_source = form.cleaned_data['input_source']
            if input_source == 'dataset':
                input = form.cleaned_data['input']
            elif input_source == 'path':
                input = Dataset(path=form.cleaned_data['input_path'],
                                owner=request.user)
                input.save()
            else:
                if input_source == 'upload':
                    # Read upload
                    input_data = form.cleaned_data['input_file'].read()
                else:
                    # Read text field
                    input_data = form.cleaned_data['input_text']
                
                name = form.cleaned_data['name']
                
                # Attempt to store on backend
                try:
                    with client.connect() as service:
                        real_path = service.storeDataset(name, input_data)
                except InternalException as ex:
                    error = WMRBackendInternalError(ex)
                except TException as ex:
                    error = WMRThriftError(ex)
                else:
                    input = Dataset(path=real_path, owner=request.user)
                    input.save()
                
                # Stop if upload failed
                if error:
                    return render_to_response('wmr/job_new.html',
                        RequestContext(request, {
                            'form': form,
                            'error': error,
                        }))
                
            
            # Handle mapper
            mapper_source = form.cleaned_data['mapper_source']
            if mapper_source == 'upload':
                mapper = form.cleaned_data['mapper_file'].read()
            else:
                mapper = form.cleaned_data['mapper']
            
            # Handle reducer
            reducer_source = form.cleaned_data['reducer_source']
            if reducer_source == 'upload':
                reducer = form.cleaned_data['reducer_file'].read()
            else:
                reducer = form.cleaned_data['reducer']
            
            
            # Create configuration object
            config = form.save(commit=False)
            config.owner = request.user
            config.input = input
            config.mapper = mapper
            config.reducer = reducer
            
            
            if request.POST['submit'] == "Save":
                # Save (or update) configuration
                saved_config = None
                try:
                    saved_config = SavedConfiguration.objects.get(
                        name=config.name, owner=request.user)
                except SavedConfiguration.MultipleObjectsReturned:
                    pass
                except SavedConfiguration.DoesNotExist:
                    saved_config = None
                        
                if saved_config:
                    # Update existing configuration
                    saved_config.update_from_other(config)
                    saved_config.touch()
                    saved_config.save()
                    flash = "Configuration successfully updated."
                else:
                    # Copy to SavedConfiguration and save
                    saved_config = SavedConfiguration()
                    saved_config.owner = request.user
                    saved_config.update_from_other(config)
                    saved_config.save()
                    flash = "Configuration succesfully saved."

                 
		# if the input source was not the dataset, the data was either already in
		# or put in a data path. Set the input field to that path.
		# (This may not be the best way to do that, but it worked.)
		if input_source != 'dataset':
		    request.POST['input_source'] = 'path'
		    request.POST['input_path'] = input.path

            else:
                # Save configuration
                config.save()
                
                # Determine whether job is test
                test = (request.POST['submit'] == 'Test')
                
                # Submit job to backend
                thrift_request = config.to_thrift_request(test)
                try:
                    with client.connect() as service:
                        backend_id = service.submit(thrift_request)
                except (ValidationException, CompilationException,
                        PermissionException, QuotaException, 
                        ForbiddenTestJobException) as ex:
                    error = WMRError(ex)
                except NotFoundException as ex:
                    error = WMRError(ex, title='Input Not Found')
                except InternalException as ex:
                    error = WMRBackendInternalError(ex)
                except TException as ex:
                    error = WMRThriftError(ex)
                else:
                    # Save job and redirect to view page
                    job = Job(config=config, owner=request.user, test=test,
                              backend_id=backend_id)
                    job.save()
                    
                    return HttpResponseRedirect(reverse(job_view, args=[job.id]))
    else:
        
        config = input = None

        if 'config' in request.GET:
            config_id = request.GET['config']
            try:
                config = Configuration.objects.get(pk=config_id)
            except Configuration.DoesNotExist as ex:
                error = WMRError(ex, title='Configuration not found')
            else:
                input = config.input
            
        elif 'output_from' in request.GET:
            from_id = request.GET['output_from']
            from_config = None
            try:
                from_config = Configuration.objects.get(id=from_id)
            except Configuration.DoesNotExist as ex:
                error = WMRError(ex, title='Configuration not found')
            else:
                config = Configuration()
                config.language = from_config.language
                config.name = from_config.name + "-phase"
                
                input_path = request.GET.get('input_path', None)
                if input_path:
                    input = Dataset(path=input_path, owner=request.user)
                    # Don't save it--just use its path below
        
        else:
            input_id = request.GET.get('input', None)
            try:
                input = Dataset.objects.get(pk=input_id)
            except Dataset.DoesNotExist:
                input = None
        
        
        # Determine correct form field for input
        formdata = {}
        if input:
            if input.public:
                formdata = {
                    'input_source': 'dataset',
                    'input': input.id,
                }
            else:
                formdata = {
                   'input_source': 'path',
                   'input_path': input.path,
                }
        
        form = ConfigurationForm(instance=config, initial=formdata)
    
    return render_to_response('wmr/job_new.html', RequestContext(request, {
        'form': form,
        'error': error,
        'flash': flash,
    }))


STATE_DISPLAYS = {
    State.PREP: 'Initializing',
    State.RUNNING: 'In Progress',
    State.SUCCESSFUL: 'Succeeded',
    State.FAILED: 'Failed',
    State.KILLED: 'Killed',
}


@login_required
def job_view(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    
    status = error = output = paginator = refresh = None
    try:
        with client.connect() as service:
            status = service.getStatus(job.backend_id)
    except NotFoundException as ex:
        error = WMRError(ex,title='Job Expired',message='This job has expired, and is unavailable.')
    except InternalException as ex:
        error = WMRBackendInternalError(ex)
    except TException as ex:
        error = WMRThriftError(ex)
    else:
        # Update cached job status
        job.update_status(status)
        job.save()
        
        # Determine whether or not a job is finished
        status.is_finished = (status.state == State.SUCCESSFUL or
                status.state == State.KILLED or status.state == State.FAILED)
        
        if not status.is_finished:
            if datetime.datetime.now() - job.submit_time > datetime.timedelta(minutes=5):
                refresh = 15
            else:
                refresh = 5
        
        # Retrieve output page if appropriate
        if (status.state == State.SUCCESSFUL and status.reduceStatus and
            status.reduceStatus.output is None and
            status.info and status.info.outputPath):
            # Check for page from request
            try:
                if 'page' in request.GET:
                    page = int(request.GET['page'])
                else:
                    page = 1
            except ValueError:
                page = 1
            
            # Fetch page
            try:
                with client.connect() as service:
                    data_page = service.readDataPage(status.info.outputPath, page)
            except (NotFoundException, PermissionException) as ex:
                error = WMRError(ex)
            except InternalException as ex:
                error = WMRBackendInternalError(ex)
            except TException as ex:
                error = WMRThriftError(ex)
            else:
                if data_page.totalPages == 0:
                    output = {
                        'data': '[Empty]',
                        'paginator': SimplePaginator(page, 1),
                    }
                else:
                    paginator = SimplePaginator(page, data_page.totalPages)
                    output = {
                        'data': data_page.data,
                        'paginator': paginator,
                    }
        
        # Set human-readable state values
        if status.state:
            status.state_display = STATE_DISPLAYS[status.state]
        if status.mapStatus and status.mapStatus.state:
            status.mapStatus.state_display = \
                STATE_DISPLAYS[status.mapStatus.state]
        if status.reduceStatus and status.reduceStatus.state:
            status.reduceStatus.state_display = \
                STATE_DISPLAYS[status.reduceStatus.state]
        
        # Create a configuration that re-uses the input
        recycle = Configuration()
        recycle.language = job.config.language
        recycle.name = job.config.name
        recycle.input = job.config.input
        
    return render_to_response('wmr/job_view.html', RequestContext(request, {
        'job': job,
        'status': status,
        'output': output,
        'error': error,
        'refresh': refresh,
    }))


@login_required
def job_list(request):
    jobs = Job.objects.filter(owner=request.user)
    return render_to_response('wmr/job_list.html', RequestContext(request, {
        'jobs': jobs
    }))

@login_required
def dataset_list(request):
    datasets = Dataset.objects.filter(owner=request.user)
    public_datasets = Dataset.objects.filter(public=True)
    return render_to_response('wmr/dataset_list.html', RequestContext(request, {
        'datasets' : datasets,
        'public_datasets' : public_datasets,
    }))

@permission_required('wmr.add_dataset')
def dataset_new(request):
    if request.method == 'POST':
        form = PublicDatasetForm(request.POST)
        if form.is_valid():
            dataset = form.save(commit=False)
            dataset.owner = request.user
            dataset.public = True
            dataset.save()
            
            return HttpResponseRedirect(reverse('wmr.views.dataset_list'))
    else:
        form = PublicDatasetForm()
    
    return render_to_response('wmr/dataset_new.html', RequestContext(request, {
        'form': form,
    }))

@permission_required('wmr.delete_dataset')
def dataset_delete(request, dataset_id):
    dataset = get_object_or_404(Dataset, pk=dataset_id)
    dataset.delete()
    return HttpResponseRedirect(reverse('wmr.views.dataset_list'))

@login_required
def job_kill(request, job_id):
        # Kill the specified job.
        job = get_object_or_404(Job, pk=job_id)
        status = error = None
        
        try:
                with client.connect() as service:
                        status = service.getStatus(job.backend_id)
                        service.kill(job.backend_id)
        except NotFoundException as ex:
                error = WMRError(ex, title='Job Not Found',
                        message="The job " + job.id + " could not be killed.")
        except IllegalJobStateException as ex:
                        error = WMRError(ex, title="Invalid job state",
                                message="The job is already complete.")
        except InternalException as ex:
                error = WMRBackendInternalError(ex)
        except TException as ex:
                error = WMRThriftError(ex)
        
        return render_to_response('wmr/job_kill.html', RequestContext(request,
        {
                'job': job,
                'status': status,
                'error': error,
        }))


@login_required
def configs(request):
    configs = SavedConfiguration.objects.filter(owner=request.user)
    public_configs = SavedConfiguration.objects.filter(public=True)
    return render_to_response('wmr/config_list.html', RequestContext(request, {
        'configs': configs,
        'public_configs': public_configs,
    }))


class SimplePaginator(object):
    def __init__(self, current_page, last_page):
        # Calculate "objects" (page numbers & ellipses) to display
        #  - Display a maximum of 9 total objects
        #  - Always the same number of objects for a given number of pages
        #  - If ellipses would skip only one number, just show number
        if last_page <= 9:
            pages = range(1, last_page + 1)
        else:
            if current_page <= 5:
                lower_page = 1
            else:
                lower_page = current_page - 2
            
            if current_page >= (last_page - 4):
                upper_page = last_page
            else:
                upper_page = current_page + 2
            
            pages = range(lower_page, upper_page + 1)
            if lower_page != 1:
                pages = [1, '...'] + pages
            if upper_page != last_page:
                pages = pages + ['...', last_page]
        
        self.pages = pages
        self.current_page = current_page
        self.last_page = last_page
        self.has_previous = (current_page != 1)
        self.has_next = (current_page != last_page)
    
    def previous_page(self):
        return self.current_page - 1
    
    def next_page(self):
        return self.current_page + 1
