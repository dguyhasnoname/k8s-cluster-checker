from kubernetes import client
from kubernetes.client.rest import ApiException
from .load_kube_config import kubeConfig

kubeConfig.load_kube_config()
core = client.CoreV1Api()

class K8sConfigMap:
    def get_cm(ns):
        try:
            if ns != 'all':
                #print ("\n[INFO] Fetching {} namespace configMaps data...".format(ns))
                namespace = ns
                configmaps = core.list_namespaced_config_map(namespace, timeout_seconds=10)
            else:
                print ("\n[INFO] Fetching all namespace configMaps data...")
                configmaps = core.list_config_map_for_all_namespaces(timeout_seconds=10)
            return configmaps
        except ApiException as e:
            print("Exception when calling CoreV1Api->list_namespaced_config_map: %s\n" % e)