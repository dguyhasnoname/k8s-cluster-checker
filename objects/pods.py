from kubernetes import client, config
from kubernetes.client.rest import ApiException
import sys, time, os, getopt, argparse
import objects as k8s
from modules.get_pods import K8sPods

start_time = time.time()
config.load_kube_config()
core = client.CoreV1Api()

def usage():
    parser=argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""This script can be used to fetch details about pods deployed \
in all namespaces ib k8s cluster.

Before running script export KUBECONFIG file as env:

    export KUBECONFIG=/Users/dguyhasnoname/kubeconfig\n""",
        epilog="""All's well that ends well.""")
    
    parser.add_argument('-v', '--verbose', type=str, help="verbose mode. \
Use this flag to get namespaced pod level config details.")
    args=parser.parse_args()

# class K8sPods:
#     def get_pods(ns):
#         try:
#             if ns == 'all':          
#                 pods = core.list_pod_for_all_namespaces(timeout_seconds=10)
#             else:
#                 namespace = ns
#                 pods = core.list_namespaced_pod(namespace, timeout_seconds=10)
#             return pods
#         except ApiException as e:
#             print("Exception when calling CoreV1Api->list_pod_for_all_namespaces: %s\n" % e)

class _Pods:
    global k8s_object, k8s_object_list, verbose
    # with alive_bar(100, bar = 'bubbles') as bar:
    #     for i in range(100):
    #         k8s_object_list = get_pods()
    #         bar()
    k8s_object_list = K8sPods.get_pods('all',core)
    k8s_object = 'pods'

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
        headers = ['NAMESPACE', 'DEPLOYMENT', 'CONTAINER_NAME', 'LIMITS', 'REQUESTS']       
        data = k8s.Check.resources(k8s_object,k8s_object_list)
        k8s.Output.print_table(data,headers,v)

    def check_pod_qos(v):
        headers = ['NAMESPACE', 'DEPLOYMENT', 'QoS']
        data = k8s.Check.qos(k8s_object,k8s_object_list)
        k8s.Output.print_table(data,headers,v)

    def check_pod_tolerations_affinity_node_selector_priority(v):
        headers = ['NAMESPACE', 'POD', 'NODE_SELECTOR', 'TOLERATIONS', 'AFFINITY', 'PRIORITY_CLASS']
        data = k8s.Check.tolerations_affinity_node_selector_priority(k8s_object,k8s_object_list)
        k8s.Output.print_table(data,headers,v)

    def check_image_pullpolicy(v):
        headers = ['DEPLOYMENT', 'CONTAINER_NAME', 'IMAGE_PULL_POLICY', 'IMAGE', 'LATEST_TAG_AVAILABLE']
        data = k8s.Check.image_pull_policy(k8s_object,k8s_object_list)
        k8s.Output.print_table(data,headers,v)

    def call_all(v):
        #_Pods.get_namespaced_pod_list(v)
        _Pods.check_pod_security(v)
        _Pods.check_pod_health_probes(v)
        _Pods.check_pod_resources(v)
        _Pods.check_pod_qos(v)
        _Pods.check_image_pullpolicy(v)
        _Pods.check_pod_tolerations_affinity_node_selector_priority(v)

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hv", ["help", "verbose"])
        if not opts:        
            _Pods.call_all("")
            
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)
        return

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-v", "--verbose"):
            verbose = True
            _Pods.call_all(verbose)
        else:
            assert False, "unhandled option"

    print(k8s.Output.GREEN + "\nTotal time taken: " + k8s.Output.RESET + \
    "{}s".format(round((time.time() - start_time), 2)))     

if __name__ == "__main__":
    main()