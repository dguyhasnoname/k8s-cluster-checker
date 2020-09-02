import sys, time, os, getopt
start_time = time.time()
from modules.main import GetOpts
from modules import logging as logger
from modules.get_ds import K8sDaemonSet
from modules import process as k8s

def usage():
    parser=argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""This script can be used to fetch details about damemonsets \
in kube-system namespace in k8s cluster.

Before running script export KUBECONFIG file as env:

    export KUBECONFIG=/Users/dguyhasnoname/kubeconfig\n""",
        epilog="""All's well that ends well.""")
    
    parser.add_argument('-v', '--verbose', type=str, \
    help="verbose mode. Use this flag to get kube-system namespace damemonset details.")
    args=parser.parse_args()

class _Daemonset:
    def __init__(self,ns):
        global k8s_object_list, namespace
        self.ns = ns
        if not ns:
            ns = 'all'
        namespace = ns
        k8s_object_list = K8sDaemonSet.get_damemonsets(ns) 
  
    global k8s_object, _logger
    _logger = logger.get_logger('_Daemonset') 
    k8s_object = 'daemonset'

    def check_damemonset_security(v, l):
        headers = ['NAMESPACE', 'DAEMONSET', 'CONTAINER_NAME', 'PRIVILEGED_ESC', \
        'PRIVILEGED', 'READ_ONLY_FS', 'RUN_AS_NON_ROOT', 'RUNA_AS_USER']        
        data = k8s.Check.security_context(k8s_object, k8s_object_list, \
        headers, v, namespace, l)
        if l: _logger.info(data)

    def check_damemonset_health_probes(v, l):
        headers = ['NAMESPACE', 'DAEMONSET', 'CONTAINER_NAME', \
        'READINESS_PROPBE', 'LIVENESS_PROBE']        
        data = k8s.Check.health_probes(k8s_object, k8s_object_list, \
        headers, v, namespace, l)
        if l: _logger.info(data)

    def check_damemonset_resources(v, l):
        headers = ['NAMESPACE', 'DAEMONSET', 'CONTAINER_NAME', \
        'LIMITS', 'REQUESTS']
        data = k8s.Check.resources(k8s_object, k8s_object_list, \
        headers, v, namespace, l)
        if l: _logger.info(data)

    def check_damemonset_tolerations_affinity_node_selector_priority(v, l):  
        headers = ['NAMESPACE', 'DAEMONSET', 'NODE_SELECTOR', \
        'TOLERATIONS', 'AFFINITY', 'PRIORITY_CLASS']
        data = k8s.Check.tolerations_affinity_node_selector_priority(\
        k8s_object, k8s_object_list, headers, v, namespace, l)
        if l: _logger.info(data)

def call_all(v, ns, l):
    _Daemonset(ns)
    _Daemonset.check_damemonset_security(v, l)
    _Daemonset.check_damemonset_health_probes(v, l)
    _Daemonset.check_damemonset_resources(v, l)
    _Daemonset.check_damemonset_tolerations_affinity_node_selector_priority(v, l)

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