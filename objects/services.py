import sys, time, os, getopt
start_time = time.time()
from modules.main import GetOpts
from modules import process as k8s
from modules.get_svc import K8sService

class _Service:
    def __init__(self,ns):
        global k8s_object_list, namespace
        self.ns = ns
        if not ns:
            ns = 'all'
        namespace = ns
        k8s_object_list = K8sService.get_svc(ns)    
    global k8s_object
    k8s_object = 'services'

    def list_service(v, l):
        headers = ['NAMESPACE', 'SERVICE', 'SERVICE_TYPE', 'CLUSTER_IP', \
        'SELECTOR']
        data = k8s.Service.get_service(k8s_object, k8s_object_list, headers, \
        v, namespace, l)
        
        data = k8s.Output.append_hyphen(data[1], '---------')
        data.append(["Total: " , len(data) - 1 , '-', '-', '-'])
        k8s.Output.print_table(data, headers, v, l)

def call_all(v, ns, l):
    _Service(ns)
    _Service.list_service(v, l)

def main():
    options = GetOpts.get_opts()
    if options[0]:
        usage()
    if options:
        call_all(options[1], options[2], options[3])
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