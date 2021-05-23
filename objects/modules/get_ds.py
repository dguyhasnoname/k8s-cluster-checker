from kubernetes import client
from kubernetes.client.rest import ApiException
from .load_kube_config import kubeConfig

kubeConfig.load_kube_config()
apps = client.AppsV1Api()

class K8sDaemonSet:
    def get_damemonsets(ns, logger):           
        try:
            if ns != 'all': 
                logger.info ("Fetching {} namespace dameonsets data...".format(ns))
                namespace = ns
                damemonsets = apps.list_namespaced_daemon_set(namespace, timeout_seconds=10)
            else:           
                logger.info ("Fetching all namespace dameonsets data...")  
                damemonsets = apps.list_daemon_set_for_all_namespaces(timeout_seconds=10)
            return damemonsets
        except ApiException as e:
            logger.info("Exception when calling AppsV1Api->list_namespaced_daemon_set: %s\n" % e)