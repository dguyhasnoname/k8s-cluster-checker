import sys, time, os, getopt
from modules import process as k8s
from modules.get_svc import K8sService

start_time = time.time()

class _Service:
    def __init__(self,ns):
        global k8s_object_list
        self.ns = ns
        if not ns:
            ns = 'all'
        k8s_object_list = K8sService.get_svc(ns)    
    global k8s_object
    k8s_object = 'services'

    def list_service(v):
        data = []
        headers = ['NAMESPACE', 'SERVICE', 'CLUSTER_IP', 'SELECTOR']
        for item in k8s_object_list.items:
            if item.spec.selector:
                for i in item.spec.selector:
                    app_label = i
                    break
                data.append([item.metadata.namespace, item.metadata.name, \
                item.spec.cluster_ip, app_label + ": " + item.spec.selector[app_label]])
            else:
                data.append([item.metadata.namespace, item.metadata.name, \
                item.spec.cluster_ip, "None"])
        data.append(['----------', '---', '---', '---'])
        data.append(["Total: " , len(data) - 1 , '-', '-'])
        k8s.Output.print_table(data,headers,True)

    def analyse_service(v):
        k8s.Service.check_service(k8s_object, k8s_object_list)

def call_all(v,ns):
    _Service(ns)
    _Service.analyse_service(v)
    if v: _Service.list_service(v)


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvn:", ["help", "verbose", "namespace"])
        if not opts:        
            call_all("","")
            sys.exit()
            
    except getopt.GetoptError as err:
        print(err)
        return
    verbose, ns = '', ''
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-v", "--verbose"):
            verbose = True
        elif o in ("-n", "--namespace"):
            if not verbose: verbose = False
            ns = a          
        else:
            assert False, "unhandled option"
    call_all(verbose,ns)
    k8s.Output.time_taken(start_time)      

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(k8s.Output.RED + "[ERROR] " + k8s.Output.RESET + 'Interrupted from keyboard!')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)    