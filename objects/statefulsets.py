from kubernetes import client, config
from kubernetes.client.rest import ApiException
import sys, time, os, getopt
import datetime
import objects as k8s

start_time = time.time()
config.load_kube_config()
apps = client.AppsV1Api()

class K8sStatefulSet:
    def get_sts(ns):
        namespace = 'kube-system'
        try:
            if ns != 'all': 
                namespace = ns            
                statefulsets = apps.list_namespaced_stateful_set(namespace, timeout_seconds=10)
            else:
                statefulsets = apps.list_stateful_set_for_all_namespaces(timeout_seconds=10)
            return statefulsets
        except ApiException as e:
            print("Exception when calling AppsV1Api->list_namespaced_stateful_set: %s\n" % e)

class _Sts:
    global k8s_object, k8s_object_list, namespace
    k8s_object_list = K8sStatefulSet.get_sts('kube-system')
    k8s_object = 'statefulsets'

    def check_sts_security(v):
        headers = ['STATEFULSET', 'CONTAINER_NAME', 'PRIVILEGED_ESC', \
        'PRIVILEGED', 'READ_ONLY_FS', 'RUN_AS_NON_ROOT', 'RUNA_AS_USER']        
        data = k8s.Check.security_context(k8s_object,k8s_object_list)
        k8s.Output.print_table(data,headers,v)

    def check_sts_health_probes(v):
        headers = ['STATEFULSET', 'CONTAINER_NAME', 'READINESS_PROPBE', 'LIVENESS_PROBE']        
        data = k8s.Check.health_probes(k8s_object,k8s_object_list)
        k8s.Output.print_table(data,headers,v)

    def check_sts_resources(v):
        headers = ['STATEFULSET', 'CONTAINER_NAME', 'LIMITS', 'REQUESTS']
        data = k8s.Check.resources(k8s_object,k8s_object_list)
        k8s.Output.print_table(data,headers,v)

    def check_sts_tolerations_affinity_node_selector_priority(v):  
        headers = ['STATEFULSET', 'NODE_SELECTOR', 'TOLERATIONS', 'AFFINITY', 'PRIORITY_CLASS']
        data = k8s.Check.tolerations_affinity_node_selector_priority(k8s_object,k8s_object_list)
        k8s.Output.print_table(data,headers,v)

def call_all(v):
    _Sts.check_sts_security(v)
    _Sts.check_sts_health_probes(v)
    _Sts.check_sts_resources(v)
    _Sts.check_sts_tolerations_affinity_node_selector_priority(v)

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

    print(k8s.Output.GREEN + "\nTotal time taken: " + k8s.Output.RESET + \
    "{}s".format(round((time.time() - start_time), 2)))     

if __name__ == "__main__":
    main()