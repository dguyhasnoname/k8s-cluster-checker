from kubernetes import client
from kubernetes.client.rest import ApiException
from .load_kube_config import kubeConfig

kubeConfig.load_kube_config()
apps = client.AppsV1Api()

class K8sStatefulSet:
    def get_sts(ns, logger):
        try:
            if ns != 'all':
                logger.info ("Fetching {} namespace statefulSets data...".format(ns)) 
                namespace = ns            
                statefulsets = apps.list_namespaced_stateful_set(namespace, timeout_seconds=10)
            else:
                logger.info ("Fetching all namespace statefulSets data...")
                statefulsets = apps.list_stateful_set_for_all_namespaces(timeout_seconds=10)
            return statefulsets
        except ApiException as e:
            logger.warning("Exception when calling AppsV1Api->list_namespaced_stateful_set: %s\n" % e)