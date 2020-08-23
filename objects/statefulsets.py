import sys, time, os, getopt
start_time = time.time()
from modules.main import GetOpts
from modules import logging as logger
from modules import process as k8s
from modules.get_sts import K8sStatefulSet

class _Sts:
    def __init__(self,ns):
        global k8s_object_list, namespace
        self.ns = ns
        if not ns:
            ns = 'all'
        namespace = ns
        k8s_object_list = K8sStatefulSet.get_sts(ns)    
    global k8s_object, _logger
    _logger = logger.get_logger('_Sts')
    k8s_object = 'statefulsets'

    def check_sts_security(v, l):
        headers = ['NAMESPACE', 'STATEFULSET', 'CONTAINER_NAME', 'PRIVILEGED_ESC', \
        'PRIVILEGED', 'READ_ONLY_FS', 'RUN_AS_NON_ROOT', 'RUNA_AS_USER']        
        data = k8s.Check.security_context(k8s_object, k8s_object_list, headers, \
        v, namespace, l)
        if l: _logger.info(data)

    def check_sts_health_probes(v, l):
        headers = ['NAMESPACE', 'STATEFULSET', 'CONTAINER_NAME', \
        'READINESS_PROPBE', 'LIVENESS_PROBE']        
        data = k8s.Check.health_probes(k8s_object, k8s_object_list, headers, \
        v, namespace, l)
        if l: _logger.info(data)

    def check_sts_resources(v, l):
        headers = ['NAMESPACE', 'STATEFULSET', 'CONTAINER_NAME', \
        'LIMITS', 'REQUESTS']
        data = k8s.Check.resources(k8s_object, k8s_object_list, headers, \
        v, namespace, l)
        if l: _logger.info(data)

    def check_sts_tolerations_affinity_node_selector_priority(v, l):  
        headers = ['NAMESPACE', 'STATEFULSET', 'NODE_SELECTOR', \
        'TOLERATIONS', 'AFFINITY', 'PRIORITY_CLASS']
        data = k8s.Check.tolerations_affinity_node_selector_priority(k8s_object, \
        k8s_object_list, headers, v, namespace, l)
        if l: _logger.info(data)

def call_all(v, ns, l):
    _Sts(ns)
    _Sts.check_sts_security(v, l)
    _Sts.check_sts_health_probes(v, l)
    _Sts.check_sts_resources(v, l)
    _Sts.check_sts_tolerations_affinity_node_selector_priority(v, l)

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