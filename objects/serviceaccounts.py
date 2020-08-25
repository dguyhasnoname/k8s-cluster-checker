import time, os, json
start_time = time.time()
from modules.main import GetOpts
from modules import logging as logger
from modules import process as k8s
from modules.get_svc_acc import K8sSvcAcc

class ServiceAccount:
    def __init__(self,ns):
        global k8s_object_list, namespace
        self.ns = ns
        if not ns:
            ns = 'all'
        namespace = ns   
        k8s_object_list = K8sSvcAcc.get_svc_acc(ns) 
    global k8s_object, _logger
    _logger = logger.get_logger('ServiceAccount')
    k8s_object = 'serviceaccount'

    def get_namespaced_pod_list(v, l):
        data = []
        headers = ['NAMESPACE', 'SERVICE_ACCOUNT', 'SECRET']
        for item in k8s_object_list.items:
            for j in item.secrets:
                data.append([item.metadata.namespace, item.metadata.name, j.name])
        if v: print ("Total service accounts: {}".format(len(data)))            
        k8s.Output.print_table(data, headers, True, l)
        return data

def call_all(v, ns, l):
    ServiceAccount(ns)
    ServiceAccount.get_namespaced_pod_list(v, l)

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