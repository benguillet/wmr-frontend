import settings
from wmr.thriftapi import JobService
from wmr.thriftapi.ttypes import *
from thrift.Thrift import TException
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.protocol import TBinaryProtocol
import logging
import contextlib

HOST = 'localhost'
PORT = 50100
try:
    from django.conf import settings
    HOST = getattr(settings, 'WMR_HOST', HOST)
    PORT = getattr(settings, 'WMR_PORT', PORT)
except ImportError:
    pass


@contextlib.contextmanager
def connect(host=HOST, port=PORT):
    transport = None
    try:
        sock = TSocket.TSocket(host, port)
        transport = TTransport.TBufferedTransport(sock)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        service = JobService.Client(protocol)
        transport.open()
        
        yield service
    finally:
        if transport:
            transport.close()


def run(cmdline_args=None):
    
    # Parse and validate options
    
    import os
    from urlparse import urlparse
    from optparse import OptionParser, OptionGroup
    usage="""Usage:
    %prog submit [global_opts] -i PATH {-m STRING|-M FILE} {-r STRING|-R FILE} \
        [[-s HOST[:PORT]] [-n NAME] [-u USER] [-l LANG] \
        [--map-tasks NUM] [--reduce-tasks NUM]]
    %prog status [global_opts] id
    %prog kill [global_opts] id
    %prog read PATH PAGE_NUM
    %prog store NAME {STRING | -F FILE}"""
    parser = OptionParser(usage=usage)
    
    globalopts = OptionGroup(parser, "Global Options")
    globalopts.add_option('-s', '--server', dest='server',
                          default=('%s:%d' % (HOST, PORT)),
                          help='Connect to HOST on PORT', metavar='HOST[:PORT]')
    
    submitopts = OptionGroup(parser, "Submit Options")
    submitopts.add_option('-n', '--name', dest='name',
                          help='Use NAME for job', metavar='NAME')
    submitopts.add_option('-u', '--user', dest='user',
                          help='Submit job as USER', metavar='USER',
                          default=os.environ['LOGNAME'])
    submitopts.add_option('-l', '--lang', dest='lang', default='python3',
                          help='Use LANG for mapper and reducer', metavar='LANG')
    
    submitopts.add_option('-i', '--input', dest='input',
                          help='Use PATH for job input', metavar='PATH')
    submitopts.add_option('-m', '--mapper', dest='mapper',
                          help='Use STRING as mapper', metavar='STRING')
    submitopts.add_option('-M', '--mapper-file', dest='mapper_file',
                          help='Read mapper from FILE', metavar='FILE')
    submitopts.add_option('-r', '--reducer', dest='reducer',
                          help='Use STRING as reducer', metavar='STRING')
    submitopts.add_option('-R', '--reducer-file', dest='reducer_file',
                          help='Read reducer from FILE', metavar='FILE')
    
    submitopts.add_option('--map-tasks', dest='map_tasks', type='int',
                          help='Request NUM map tasks', metavar='NUM')
    submitopts.add_option('--reduce-tasks', dest='reduce_tasks', type='int',
                          help='Request NUM reduce tasks', metavar='NUM',
                          default=1)
    submitopts.add_option('-t', '--test', action='store_true', dest='isTest',
                          help='Submit the job as a test job',
			  metavar='BOOL', default=False)
    
    storeopts = OptionGroup(parser, "Store Options")
    storeopts.add_option('-F', '--file', dest='file',
                         help='Upload FILE instead of STRING', metavar='FILE')
    
    parser.add_option_group(globalopts)
    parser.add_option_group(submitopts)
    parser.add_option_group(storeopts)
    
    (options, args) = parser.parse_args()
    
    if len(args) < 1:
        parser.error('Please specify a command')
    server = urlparse('//' + options.server)
    if server.hostname is None:
        parser.error('Invalid server spec \'%s\'' % options.server)
    
    
    # Setup logging
    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)s [%(lineno)d]: %(message)s')
    
    # Call appropriate command handler
    handler = None
    if args[0] == 'submit':
        handler = _run_submit
    elif args[0] == 'status':
        handler = _run_status
    elif args[0] == 'kill':
        handler = _run_kill
    elif args[0] == 'read':
        handler = _run_read
    elif args[0] == 'store':
        handler = _run_store
    else:
        parser.error('Invalid command %s' % args[0])
    handler(server, parser, options, args[1:])


def _run_submit(server, parser, options, args):
    # Validate arguments
    if options.input is None:
        parser.error('Please specify an input path.')
    if options.mapper is None and options.mapper_file is None:
        parser.error('Please specify a mapper using -m or -M')
    if options.mapper is not None and options.mapper_file is not None:
        parser.error('The -m and -M options are mutually exclusive')
    if options.reducer is None and options.reducer_file is None:
        parser.error('Please specify a reducer using -r or -R')
    if options.reducer is not None and options.reducer_file is not None:
        parser.error('The -r and -R options are mutually exclusive')
    
    
    # Get reducer/mapper file if appropriate
    if options.mapper is not None:
        mapper = options.mapper
    else:
        with open(options.mapper_file) as file:
            mapper = file.read()
    
    if options.reducer is not None:
        reducer = options.reducer
    else:
        with open(options.reducer_file) as file:
            reducer = file.read()
    
    
    # Connect and submit
    job = JobRequest(name=options.name, user=options.user,
                     language=options.lang, input=options.input,
                     mapper=mapper, reducer=reducer,
                     mapTasks=options.map_tasks,
                     reduceTasks=options.reduce_tasks, test=options.isTest)
    
    logging.info('Submitting job: %s', job)
    id = _make_request(lambda service: service.submit(job))
    logging.info('Server returned job ID %d', id)


def _run_status(server, parser, options, args):
    # Validate arguments
    if len(args) < 1:
        parser.error("Please specify job ID returned by submit command")
    elif len(args) > 1:
        parser.error("Unrecognized positional arguments %s" % args)
    try:
        id = int(args[0])
    except ValueError:
        parser.error("Invalid job id %s. Please enter a number." % args[0])
    
    # Connect and check status
    logging.info('Retrieving status for job %d', id)
    status = _make_request(lambda service: service.getStatus(id))
    
    logging.info('Server returned status:')
    logging.info('  State: %s', State._VALUES_TO_NAMES[status.state])
    logging.info('  Map Status:')
    if status.mapStatus is None:
        logging.info('    [None]')
    else:
        logging.info('    Progress: %d%%', status.mapStatus.progress)
        logging.info('    State: %s', State._VALUES_TO_NAMES[status.mapStatus.state])
        logging.info('    Exit Code: %s', status.mapStatus.code)
        logging.info('    Output Path: %s', status.mapStatus.outputPath)
        logging.info('    Output:\n======\n%s\n======', status.mapStatus.output)
        logging.info('    Errors:\n======\n%s\n======', status.mapStatus.errors)
    logging.info('  Reduce Status:')
    if status.reduceStatus is None:
        logging.info('    [None]')
    else:
        logging.info('    Progress: %d%%', status.reduceStatus.progress)
        logging.info('    State: %s', State._VALUES_TO_NAMES[status.reduceStatus.state])
        logging.info('    Exit Code: %s', status.reduceStatus.code)
        logging.info('    Output Path: %s', status.reduceStatus.outputPath)
        logging.info('    Output:\n======\n%s\n======', status.reduceStatus.output)
        logging.info('    Errors:\n======\n%s\n======', status.reduceStatus.errors)
    logging.info('  Info:')
    if status.info is None:
        logging.info('    [None]')
    else:
        logging.info('    Native ID: %s', status.info.nativeID)
        logging.info('    Name: %s', status.info.name)
        logging.info('    Test: %s', status.info.test)
        logging.info('    Input Path: %s', status.info.inputPath)
        logging.info('    Output Path: %s', status.info.outputPath)
        logging.info('    Mapper:\n======\n%s\n======', status.info.mapper)
        logging.info('    Reducer:\n======\n%s\n======', status.info.reducer)
        logging.info('    Map Tasks: %d', status.info.requestedMapTasks)
        logging.info('    Reduce Tasks: %d', status.info.requestedMapTasks)

def _run_read(server, parser, options, args):
    # Validate arguments
    if len(args) < 1:
        parser.error("Please specify path")
    elif len(args) > 2:
        parser.error("Unrecognized positional arguments %s" % args)
    path = args[0]
    page = 0
    if len(args) == 2:
        try:
            page = int(args[1])
        except ValueError:
            parser.error("Invalid page %s. Please enter a number." % args[0])
    
    # Connect and retrieve page
    logging.info('Retrieving file %s', path)
    dataPage = _make_request(lambda service: service.readDataPage(path, page))
    logging.info('Page %d of %d:\n======\n%s\n======', 
                 page, dataPage.totalPages, dataPage.data)


def _run_store(server, parser, options, args):
    # Validate arguments
    if options.file is None:
        if len(args) < 2:
            parser.error("Please specify file name and data to upload")
        elif len(args) > 2:
            parser.error("Unrecognized positional arguments %s" % args)
        data = args[1]
    else:
        if len(args) < 1:
            parser.error("Please specify file name")
        elif len(args) == 2:
            parser.error("Please specify data EITHER via the command line or with the -F option")
        
        with open(options.file) as data_file:
            data = data_file.read()
    name = args[0]
    
    
    # Connect and retrieve page
    logging.info('Uploading data')
    stored_name = _make_request(lambda service: service.storeDataset(name, data))
    logging.info('Successfully uploaded to %s', stored_name)


def _run_kill(server, parser, options, args):
    # Validate arguments
    if len(args) < 1:
        parser.error("Please specify job ID returned by submit command")
    elif len(args) > 1:
        parser.error("Unrecognized positional arguments %s" % args)
    try:
        id = int(args[0])
    except ValueError:
        parser.error("Invalid job id %s. Please enter a number." % args[0])
    
    
    # Connect and retrieve page
    logging.info('Attempting to kill job %d', id)
    _make_request(lambda service: service.kill(id))
    logging.info('Successfully killed job %d', id)


def _make_request(request_functor):
    """Calls request_functor and handles Thrift-related errors appropriately."""
    
    try:
        with connect() as service:
            return request_functor(service)
    except InternalException as ex:
        logging.error('Server encountered internal error:')
        logging.error('\t%s', ex.message)
        for cause in ex.causes:
            logging.error('Caused by:')
            logging.error('\t%s', cause.stackTrace)
            exit(3)
    except (ValidationException, NotFoundException, CompilationException,
            PermissionException, IllegalJobStateException) as ex:
        logging.error('Server returned error:')
        logging.error('\t%s: %s', type(ex).__name__, ex.message)
        exit(1)
    except TException as ex:
        logging.error('Internal Thrift error:')
        logging.exception(ex)
        exit(4)

if __name__ == '__main__':
    run()
