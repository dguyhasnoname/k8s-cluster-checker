import sys, time, os, getopt, argparse
import objects as k8s
from modules.get_pods import K8sPods

start_time = time.time()

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
    parser.add_argument('-n', '--namespace', help="namepsace selector. \
Use this flag to get namespaced pod details. If this flag is not \
used, all namespace details is returned")
    args=parser.parse_args()

class _Pods:
    def __init__(self,ns):
        global k8s_object_list
        self.ns = ns
        if not ns:
            ns = 'all'   
        k8s_object_list = K8sPods.get_pods(ns) 
    global k8s_object
    k8s_object = 'pods'
    # with alive_bar(100, bar = 'bubbles') as bar:
    #     for i in range(100):
    #         k8s_object_list = get_pods()
    #         bar()

    def get_namespaced_pod_list(v):
        data = []
        headers = ['NAMESPACE', 'POD']
        for item in k8s_object_list.items:
            data.append([item.metadata.namespace, item.metadata.name])
        if v: print ("Total pods: {}".format(len(data)))            
        k8s.Output.print_table(data,headers,v)
        return data
    
    def check_pod_security(v):
        headers = ['NAMESPACE', 'POD', 'CONTAINER_NAME', 'PRIVILEGED_ESC', \
        'PRIVILEGED', 'READ_ONLY_FS', 'RUN_AS_NON_ROOT', 'RUNA_AS_USER']        
        data = k8s.Check.security_context(k8s_object,k8s_object_list)
        k8s.Output.print_table(data,headers,v)    

    def check_pod_health_probes(v):
        headers = ['NAMESPACE', 'POD', 'CONTAINER_NAME', 'READINESS_PROPBE', 'LIVENESS_PROBE']        
        data = k8s.Check.health_probes(k8s_object,k8s_object_list)
        k8s.Output.print_table(data,headers,v)  

    def check_pod_resources(v):
        headers = ['NAMESPACE', 'POD', 'CONTAINER_NAME', 'LIMITS', 'REQUESTS']       
        data = k8s.Check.resources(k8s_object,k8s_object_list)
        k8s.Output.print_table(data,headers,v)

    def check_pod_qos(v):
        headers = ['NAMESPACE', 'POD', 'QoS']
        data = k8s.Check.qos(k8s_object,k8s_object_list)
        k8s.Output.print_table(data,headers,v)

    def check_pod_tolerations_affinity_node_selector_priority(v):
        headers = ['NAMESPACE', 'POD', 'NODE_SELECTOR', 'TOLERATIONS', 'AFFINITY', 'PRIORITY_CLASS']
        data = k8s.Check.tolerations_affinity_node_selector_priority(k8s_object,k8s_object_list)
        k8s.Output.print_table(data,headers,v)

    def check_image_pull_policy(v):
        headers = ['DEPLOYMENT', 'CONTAINER_NAME', 'IMAGE_PULL_POLICY', 'IMAGE', 'LATEST_TAG_AVAILABLE']
        data = k8s.Check.image_pull_policy(k8s_object,k8s_object_list)
        k8s.Output.print_table(data,headers,v)

def call_all(v,ns):
    _Pods(ns)
    _Pods.check_pod_security(v)
    _Pods.check_pod_health_probes(v)
    _Pods.check_pod_resources(v)
    _Pods.check_pod_qos(v)
    _Pods.check_image_pull_policy(v)
    _Pods.check_pod_tolerations_affinity_node_selector_priority(v)

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