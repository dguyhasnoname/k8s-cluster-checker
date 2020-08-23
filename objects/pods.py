import time, os, argparse
start_time = time.time()
from modules.main import GetOpts
from modules import logging as logger
from modules import process as k8s
from modules.get_pods import K8sPods

def usage():
    parser=argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""This script can be used to fetch details about pods deployed \
in namespaces in k8s cluster.

Before running script export KUBECONFIG file as env:
    export KUBECONFIG=<kubeconfig file location>
    
    e.g. export KUBECONFIG=/Users/dguyhasnoname/kubeconfig\n""",
        epilog="""All's well that ends well.""")
    
    parser.add_argument('-v', '--verbose', action="store_true", help="verbose mode. \
Use this flag to get namespaced pod level config details.")
    parser.add_argument('-n', '--namespace', help="namespace selector. \
Use this flag to get namespaced pod details. If this flag is not \
used, all namespace details is returned")
    args=parser.parse_args()

class _Pods:
    def __init__(self,ns):
        global k8s_object_list, namespace
        self.ns = ns
        if not ns:
            ns = 'all'
        namespace = ns   
        k8s_object_list = K8sPods.get_pods(ns) 
    global k8s_object, _logger
    _logger = logger.get_logger('_Pods')
    k8s_object = 'pods'

    def get_namespaced_pod_list(v, l):
        data = []
        headers = ['NAMESPACE', 'POD']
        for item in k8s_object_list.items:
            data.append([item.metadata.namespace, item.metadata.name])
        if v: print ("Total pods: {}".format(len(data)))            
        k8s.Output.print_table(data,headers,v)
        return json.dumps(data)
    
    def check_pod_security(v, l):
        headers = ['NAMESPACE', 'POD', 'CONTAINER_NAME', 'PRIVILEGED_ESC', \
        'PRIVILEGED', 'READ_ONLY_FS', 'RUN_AS_NON_ROOT', 'RUNA_AS_USER']        
        data = k8s.Check.security_context(k8s_object, k8s_object_list, headers, \
        v, namespace, l)
        if l: _logger.info(data)

    def check_pod_health_probes(v, l):
        headers = ['NAMESPACE', 'POD', 'CONTAINER_NAME', 'READINESS_PROPBE', \
        'LIVENESS_PROBE']
        data = k8s.Check.health_probes(k8s_object, k8s_object_list, headers, \
        v, namespace, l)
        if l: _logger.info(data)

    def check_pod_resources(v, l):
        headers = ['NAMESPACE', 'POD', 'CONTAINER_NAME', 'LIMITS', 'REQUESTS']
        data = k8s.Check.resources(k8s_object, k8s_object_list, headers, \
        v, namespace, l)
        if l: _logger.info(data)

    def check_pod_qos(v, l):
        headers = ['NAMESPACE', 'POD', 'QoS']
        data = k8s.Check.qos(k8s_object, k8s_object_list, headers, v, namespace, l)
        if l: _logger.info(data)

    def check_pod_tolerations_affinity_node_selector_priority(v, l):
        headers = ['NAMESPACE', 'POD', 'NODE_SELECTOR', 'TOLERATIONS', \
        'AFFINITY', 'PRIORITY_CLASS']
        data = k8s.Check.tolerations_affinity_node_selector_priority(k8s_object, \
        k8s_object_list, headers, v, namespace, l)
        if l: _logger.info(data)

    def check_image_pull_policy(v, l):
        headers = ['DEPLOYMENT', 'CONTAINER_NAME', 'IMAGE', 'IMAGE_PULL_POLICY']
        data = k8s.Check.image_pull_policy(k8s_object, k8s_object_list, headers, \
        v, namespace, l)
        if l: _logger.info(data)

def call_all(v, ns, l):
    _Pods(ns)
    _Pods.check_pod_security(v, l)
    _Pods.check_pod_health_probes(v, l)
    _Pods.check_pod_resources(v, l)
    _Pods.check_pod_qos(v, l)
    _Pods.check_image_pull_policy(v, l)
    _Pods.check_pod_tolerations_affinity_node_selector_priority(v, l)

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