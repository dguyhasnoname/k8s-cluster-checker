from kubernetes import client
from kubernetes.client.rest import ApiException
from .load_kube_config import kubeConfig

kubeConfig.load_kube_config()
networking = client.NetworkingV1beta1Api()

class K8sIngress:
    def get_ingress(ns, logger):           
        try:
            if ns != 'all':
                logger.info ("Fetching {} namespace ingress data...".format(ns)) 
                namespace = ns
                ingress = networking.list_namespaced_ingress(namespace, timeout_seconds=5)
            else:
                logger.info ("Fetching all namespace ingress data...") 
                ingress = networking.list_ingress_for_all_namespaces(timeout_seconds=5)
            return ingress
        except ApiException as e:
            logger.warning ("Exception when calling NetworkingV1beta1Api->list_namespaced_ingress: %s\n" % e)
