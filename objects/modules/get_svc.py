from kubernetes import client
from kubernetes.client.rest import ApiException
from .load_kube_config import kubeConfig

kubeConfig.load_kube_config()
core = client.CoreV1Api()

class K8sService:
    def get_svc(ns, logger):
        try:
            if ns != 'all': 
                logger.info ("Fetching {} namespace services data...".format(ns))
                namespace = ns            
                services = core.list_namespaced_service(namespace, timeout_seconds=10)
            else:
                logger.info ("Fetching all namespace services data...")
                services = core.list_service_for_all_namespaces(timeout_seconds=10)
            return services
        except ApiException as e:
            logger.warning("Exception when calling AppsV1Api->list_namespaced_service: %s\n" % e)