import sys, time, os, getopt
from modules import process as k8s
from modules.get_svc import K8sService

start_time = time.time()

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
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvn:l", \
        ["help", "verbose", "namespace", "logging"])
        if not opts:        
            call_all('', '', '')
            k8s.Output.time_taken(start_time)
            sys.exit()
            
    except getopt.GetoptError as err:
        print(err)
        return
    verbose, ns, l = '', '', ''
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-v", "--verbose"):
            verbose = True
        elif o in ("-n", "--namespace"):
            ns = a
        elif o in ("-l", "--logging"):
            l = True                    
        else:
            assert False, "unhandled option"
    call_all(verbose, ns, l)
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