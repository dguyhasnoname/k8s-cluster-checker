from kubernetes import client, config
from kubernetes.client.rest import ApiException
import sys, time, os, getopt
import objects as k8s
from modules.get_ds import K8sDaemonSet

start_time = time.time()
config.load_kube_config()
apps = client.AppsV1Api()

def usage():
    parser=argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""This script can be used to fetch details about damemonsets \
        in kube-system namespace in k8s cluster.

Before running script export KUBECONFIG file as env:

    export KUBECONFIG=/Users/dguyhasnoname/kubeconfig\n""",
        epilog="""All's well that ends well.""")
    
    parser.add_argument('-v', '--verbose', type=str, help="verbose mode. Use this flag to get kube-system namespace damemonset details.")
    args=parser.parse_args()

class _Daemonset:
    global k8s_object, k8s_object_list, namespace
    k8s_object_list = K8sDaemonSet.get_damemonsets('kube-system',apps)
    k8s_object = 'daemonset'

    def check_damemonset_security(v):
        headers = ['NAMESPACE', 'DAEMONSET', 'CONTAINER_NAME', 'PRIVILEGED_ESC', \
        'PRIVILEGED', 'READ_ONLY_FS', 'RUN_AS_NON_ROOT', 'RUNA_AS_USER']        
        data = k8s.Check.security_context(k8s_object,k8s_object_list)
        k8s.Output.print_table(data,headers,v)

    def check_damemonset_health_probes(v):
        headers = ['NAMESPACE', 'DAEMONSET', 'CONTAINER_NAME', 'READINESS_PROPBE', 'LIVENESS_PROBE']        
        data = k8s.Check.health_probes(k8s_object,k8s_object_list)
        k8s.Output.print_table(data,headers,v)

    def check_damemonset_resources(v):
        headers = ['NAMESPACE', 'DAEMONSET', 'CONTAINER_NAME', 'LIMITS', 'REQUESTS']
        data = k8s.Check.resources(k8s_object,k8s_object_list)
        k8s.Output.print_table(data,headers,v)

    def check_damemonset_tolerations_affinity_node_selector_priority(v):  
        headers = ['DAEMONSET', 'NODE_SELECTOR', 'TOLERATIONS', 'AFFINITY', 'PRIORITY_CLASS']
        data = k8s.Check.tolerations_affinity_node_selector_priority(k8s_object,k8s_object_list)
        k8s.Output.print_table(data,headers,v)

def call_all(v):
    _Daemonset.check_damemonset_security(v)
    _Daemonset.check_damemonset_health_probes(v)
    _Daemonset.check_damemonset_resources(v)
    _Daemonset.check_damemonset_tolerations_affinity_node_selector_priority(v)

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hv", ["help", "verbose"])
        if not opts:        
            call_all("")
            
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)
        return

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-v", "--verbose"):
            verbose = True
            call_all(verbose)
        else:
            assert False, "unhandled option"

    print(k8s.Output.GREEN + "Total time taken: " + k8s.Output.RESET + \
    "{}s".format(round((time.time() - start_time), 2)))

if __name__ == "__main__":
    main()           