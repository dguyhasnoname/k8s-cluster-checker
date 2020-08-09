import sys, time, os, getopt
from modules import process as k8s
from modules.get_sts import K8sStatefulSet

start_time = time.time()

class _Sts:
    def __init__(self,ns):
        global k8s_object_list, namespace
        self.ns = ns
        if not ns:
            ns = 'all'
        namespace = ns
        k8s_object_list = K8sStatefulSet.get_sts(ns)    
    global k8s_object
    k8s_object = 'statefulsets'

    def check_sts_security(v):
        headers = ['NAMESPACE', 'STATEFULSET', 'CONTAINER_NAME', 'PRIVILEGED_ESC', \
        'PRIVILEGED', 'READ_ONLY_FS', 'RUN_AS_NON_ROOT', 'RUNA_AS_USER']        
        k8s.Check.security_context(k8s_object, k8s_object_list, headers, \
        v, namespace)

    def check_sts_health_probes(v):
        headers = ['NAMESPACE', 'STATEFULSET', 'CONTAINER_NAME', \
        'READINESS_PROPBE', 'LIVENESS_PROBE']        
        k8s.Check.health_probes(k8s_object, k8s_object_list, headers, \
        v, namespace)

    def check_sts_resources(v):
        headers = ['NAMESPACE', 'STATEFULSET', 'CONTAINER_NAME', \
        'LIMITS', 'REQUESTS']
        k8s.Check.resources(k8s_object, k8s_object_list, headers, \
        v, namespace)

    def check_sts_tolerations_affinity_node_selector_priority(v):  
        headers = ['NAMESPACE', 'STATEFULSET', 'NODE_SELECTOR', \
        'TOLERATIONS', 'AFFINITY', 'PRIORITY_CLASS']
        k8s.Check.tolerations_affinity_node_selector_priority(k8s_object, \
        k8s_object_list, headers, v, namespace)

def call_all(v,ns):
    _Sts(ns)
    _Sts.check_sts_security(v)
    _Sts.check_sts_health_probes(v)
    _Sts.check_sts_resources(v)
    _Sts.check_sts_tolerations_affinity_node_selector_priority(v)

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], \
        "hvn:", ["help", "verbose", "namespace"])
        if not opts:        
            call_all("","")
            k8s.Output.time_taken(start_time)
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
    main()