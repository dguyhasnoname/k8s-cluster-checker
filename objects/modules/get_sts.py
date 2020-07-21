from kubernetes import client, config
from kubernetes.client.rest import ApiException

class K8sStatefulSet:
    def get_sts(ns,apps):
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