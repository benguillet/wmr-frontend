import logging
from wmr.thriftapi import JobService
from wmr.thriftapi.ttypes import JobStatus, State, PhaseStatus, DataPage, JobInfo
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

class MockJobService(JobService.Iface):
    def storeDataset(self, name, data):
        return "/data/foo/nowhere"
    
    def readDataPage(self, path, page):
        dataPage = DataPage()
        dataPage.data = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc
        vulputate, ligula eu aliquet pretium, mi mi posuere nisi, consequat
        dictum mi nibh quis dui. Nullam urna dui, molestie vel aliquam vel,
        semper eu libero. Sed ac molestie erat. Cum sociis natoque penatibus et
        magnis dis parturient montes, nascetur ridiculus mus. Sed velit tortor,
        consequat et commodo sed, interdum ut leo. In non orci magna. Nulla
        facilisi. Sed pharetra justo ut enim semper convallis. Praesent rutrum
        faucibus nulla, ut dignissim neque mollis et. Mauris eu massa purus, in
        elementum dolor. Aliquam erat volutpat. Aliquam fringilla fringilla
        massa, quis malesuada risus dictum."""
        dataPage.totalPages = 10
    
    def submit(self, request):
        return 10010101
    
    def getInfo(self, id):
        info = JobInfo()
        info.name = 'foo'
        info.nativeID = 'job_ZZZZZZZZZZ_ZZZZ'
        info.test = False
        info.inputPath = '/data/foo/nowhere'
        info.mapper = 'def mapper(key, val): pass'
        info.reducer = 'def reducer(key, vals): pass'
        info.requestedMapTasks = 30
        info.requestedReduceTasks = 5
    
    def getStatus(self, id):
        status = JobStatus()
        status.state = State.RUNNING
        status.info = self.getInfo(id)
        status.mapStatus = PhaseStatus()
        status.mapStatus.code = 0
        status.mapStatus.progress = 65.5
        status.mapStatus.outputPath = "/data/foo/nowhere"
        status.mapStatus.errors = "It's alive!"
        status.reduceStatus = status.mapStatus
        return status
    
    def kill(self, id):
        return

def run(host='localhost', port=9090):
    mock = MockJobService()
    processor = JobService.Processor(mock)
    transport = TSocket.TServerSocket(port)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    
    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    logging.info("About to listen on %s:%d" % (host, port))
    server.serve()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    port = None
    import sys
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    run(port)
