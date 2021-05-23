import sys, time, os, getopt
start_time = time.time()
from modules.main import GetOpts
from modules.logging import Logger
from modules import process as k8s
from modules.get_svc import K8sService

class _Service:
    def __init__(self, namespace, logger):
        self.namespace = namespace
        self.logger = logger
        if not self.namespace:
            self.namespace = 'all'
        self.k8s_object_list = K8sService.get_svc(self.namespace, self.logger)    
        self.k8s_object = 'services'

    def list_service(self, v, l):
        headers = ['NAMESPACE', 'SERVICE', 'SERVICE_TYPE', 'CLUSTER_IP', \
        'SELECTOR']
        data = k8s.Service.get_service(self.k8s_object, self.k8s_object_list, headers, \
        v, self.namespace, l, self.logger)
        
        data = k8s.Output.append_hyphen(data[1], '---------')
        data.append(["Total: " , len(data) - 1 , '-', '-', '-'])
        k8s.Output.print_table(data, headers, v, l)

def call_all(v, namespace, l, logger):
    call = _Service(namespace, logger)
    call.list_service(v, l)

def main():
    options = GetOpts.get_opts()
    logger = Logger.get_logger(options[4], options[5])
    if options[0]:
        usage()
    if options:
        call_all(options[1], options[2], options[3], logger)
        k8s.Output.time_taken(start_time)      

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(k8s.Output.RED + "[ERROR] " \
        + k8s.Output.RESET + 'Interrupted from keyboard!')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)    