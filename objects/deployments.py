import sys, os, getopt, time
from time import sleep
from modules import process as k8s
from modules.get_deploy import K8sDeploy

start_time = time.time()

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

    global k8s_object
    k8s_object = 'deployments'  

    def check_deployment_security(v):
        headers = ['NAMESPACE', 'DEPLOYMENT', 'CONTAINER_NAME', 'PRIVILEGED_ESC', \
        'PRIVILEGED', 'READ_ONLY_FS', 'RUN_AS_NON_ROOT', 'RUNA_AS_USER']        
        k8s.Check.security_context(k8s_object, k8s_object_list, headers, \
        v, namespace)

    def check_deployment_health_probes(v):
        headers = ['NAMESPACE', 'DEPLOYMENT', 'CONTAINER_NAME', \
        'READINESS_PROPBE', 'LIVENESS_PROBE']        
        k8s.Check.health_probes(k8s_object, k8s_object_list, headers, \
        v, namespace)  

    def check_deployment_resources(v): 
        headers = ['NAMESPACE', 'DEPLOYMENT', 'CONTAINER_NAME', 'LIMITS', \
        'REQUESTS']       
        k8s.Check.resources(k8s_object, k8s_object_list, headers, v, namespace)

    def check_deployment_strategy(v): 
        headers = ['DEPLOYMENT', 'STRATEGY_TYPE']
        k8s.Check.strategy(k8s_object, k8s_object_list, headers, v, namespace)

    def check_replica(v): 
        headers = ['NAMESPACE', 'DEPLOYMENT', 'REPLICA_COUNT']
        k8s.Check.replica(k8s_object, k8s_object_list, headers, v, namespace)         

    def check_deployment_tolerations_affinity_node_selector_priority(v): 
        headers = ['NAMESPACE', 'DEPLOYMENT', 'NODE_SELECTOR', 'TOLERATIONS', \
        'AFFINITY', 'PRIORITY_CLASS']     
        k8s.Check.tolerations_affinity_node_selector_priority(k8s_object, \
        k8s_object_list, headers, v, namespace)       

def call_all(v,ns):
    _Deployment(ns)
    _Deployment.check_deployment_security(v)
    _Deployment.check_deployment_health_probes(v)
    _Deployment.check_deployment_resources(v)
    _Deployment.check_deployment_strategy(v)
    _Deployment.check_replica(v)
    _Deployment.check_deployment_tolerations_affinity_node_selector_priority(v)

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvn:", ["help", "verbose", \
        "namespace"])
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
    try:
        main()
    except KeyboardInterrupt:
        print(k8s.Output.RED + "[ERROR] " + k8s.Output.RESET + 'Interrupted from keyboard!')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)