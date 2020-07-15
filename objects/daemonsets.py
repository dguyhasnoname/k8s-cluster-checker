from kubernetes import client, config
from kubernetes.client.rest import ApiException
import sys, time, os 
import datetime
import objects as k8s

start_time = time.time()
config.load_kube_config()
apps = client.AppsV1Api()

class Daemonset:
    global k8s_object, k8s_object_list, namespace
    def get_damemonsets():
        namespace = 'kube-system'
        try:
            damemonsets = apps.list_namespaced_daemon_set(namespace, timeout_seconds=10)
            return damemonsets
        except ApiException as e:
            print("Exception when calling AppsV1Api->list_namespaced_daemon_set: %s\n" % e)

    k8s_object_list = get_damemonsets()
    k8s_object = 'daemonset'

    def check_damemonset_security():
        headers = ['DAEMONSET', 'CONTAINER_NAME', 'PRIVILEGED_ESC', \
        'PRIVILEGED', 'READ_ONLY_FS', 'RUN_AS_NON_ROOT', 'RUNA_AS_USER']        
        data = k8s.Check.security_context(k8s_object,k8s_object_list)
        k8s.Output.print_table(data,headers)

    def check_damemonset_health_probes():
        headers = ['DAEMONSET', 'CONTAINER_NAME', 'READINESS_PROPBE', 'LIVENESS_PROBE']        
        data = k8s.Check.health_probes(k8s_object,k8s_object_list)
        k8s.Output.print_table(data,headers)

    def check_damemonset_resources():
        headers = ['DAEMONSET', 'CONTAINER_NAME', 'LIMITS', 'REQUESTS']
        data = k8s.Check.resources(k8s_object,k8s_object_list)
        k8s.Output.print_table(data,headers)

    def check_damemonset_tolerations_affinity_node_selector_priority():  
        headers = ['DAEMONSET', 'NODE_SELECTOR', 'TOLERATIONS', 'AFFINITY', 'PRIORITY_CLASS']
        data = k8s.Check.tolerations_affinity_node_selector_priority(k8s_object,k8s_object_list)
        k8s.Output.print_table(data,headers)

def main():
    Daemonset.check_damemonset_security()
    Daemonset.check_damemonset_health_probes()
    Daemonset.check_damemonset_resources()
    Daemonset.check_damemonset_tolerations_affinity_node_selector_priority()
    print(k8s.Output.GREEN + "Total time taken: " + k8s.Output.RESET + "{}s".format(round((time.time() - start_time), 2)))

if __name__ == "__main__":
    main()           