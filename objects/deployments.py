import sys, os, getopt, time, json
from time import sleep
start_time = time.time()
from modules import logging as logger
from modules import process as k8s
from modules.get_deploy import K8sDeploy

def usage():
    parser=argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""This script can be used to fetch details about deployments \
        in kube-system namespace in k8s cluster.

Before running script export KUBECONFIG file as env:

    export KUBECONFIG=/Users/dguyhasnoname/kubeconfig\n""",
        epilog="""All's well that ends well.""")
    
    parser.add_argument('-v', '--verbose', type=str, \
    help="verbose mode. Use this flag to get kube-system namespace deployment details.")
    args=parser.parse_args()

class _Deployment:
    def __init__(self,ns):
        global k8s_object_list, namespace
        self.ns = ns
        if not ns:
            ns = 'all'
        namespace = ns
        k8s_object_list = K8sDeploy.get_deployments(ns)

    global k8s_object, _logger
    _logger = logger.get_logger('_Deployment') 
    k8s_object = 'deployments'

    def check_deployment_security(v,l):
        headers = ['NAMESPACE', 'DEPLOYMENT', 'CONTAINER_NAME', 'PRIVILEGED_ESC', \
        'PRIVILEGED', 'READ_ONLY_FS', 'RUN_AS_NON_ROOT', 'RUNA_AS_USER']        
        data = k8s.Check.security_context(k8s_object, k8s_object_list, headers, \
        v, namespace, l)
        if l: _logger.info(data)

    def check_deployment_health_probes(v,l):
        headers = ['NAMESPACE', 'DEPLOYMENT', 'CONTAINER_NAME', \
        'READINESS_PROPBE', 'LIVENESS_PROBE']        
        data = k8s.Check.health_probes(k8s_object, k8s_object_list, headers, \
        v, namespace, l)  
        if l: _logger.info(data)

    def check_deployment_resources(v,l): 
        headers = ['NAMESPACE', 'DEPLOYMENT', 'CONTAINER_NAME', 'LIMITS', \
        'REQUESTS']       
        data = k8s.Check.resources(k8s_object, k8s_object_list, \
        headers, v, namespace, l)
        if l: _logger.info(data)

    def check_deployment_strategy(v,l): 
        headers = ['DEPLOYMENT', 'STRATEGY_TYPE']
        data = k8s.Check.strategy(k8s_object, k8s_object_list, headers, \
        v, namespace, l)
        if l: _logger.info(data)

    def check_replica(v,l): 
        headers = ['NAMESPACE', 'DEPLOYMENT', 'REPLICA_COUNT']
        data = k8s.Check.replica(k8s_object, k8s_object_list, headers,\
        v, namespace, l)         
        if l: _logger.info(data)

    def check_deployment_tolerations_affinity_node_selector_priority(v,l): 
        headers = ['NAMESPACE', 'DEPLOYMENT', 'NODE_SELECTOR', 'TOLERATIONS', \
        'AFFINITY', 'PRIORITY_CLASS']     
        data = k8s.Check.tolerations_affinity_node_selector_priority(k8s_object, \
        k8s_object_list, headers, v, namespace, l)  
        if l: _logger.info(data)     

def call_all(v,ns,l):
    _Deployment(ns)
    _Deployment.check_deployment_security(v,l)
    _Deployment.check_deployment_health_probes(v,l)
    _Deployment.check_deployment_resources(v,l)
    _Deployment.check_deployment_strategy(v,l)
    _Deployment.check_replica(v,l)
    _Deployment.check_deployment_tolerations_affinity_node_selector_priority(v,l)

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvn:l", ["help", "verbose", \
        "namespace", "logging"])
        if not opts:        
            call_all('','','')
            k8s.Output.time_taken(start_time)
            sys.exit()
            
    except getopt.GetoptError as err:
        print(err)
        return
    verbose, ns, l= '', '', ''
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