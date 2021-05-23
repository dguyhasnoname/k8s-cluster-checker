from kubernetes import client
from kubernetes.client.rest import ApiException
from .load_kube_config import kubeConfig

kubeConfig.load_kube_config()
crd = client.ApiextensionsV1beta1Api()

class K8sCRDs:
    def get_crds(logger):
        try:
            logger.info ("Fetching all crds data...")
            crds = crd.list_custom_resource_definition(timeout_seconds=10)
            return crds
        except ApiException as e:
            logger.warning("Exception when calling ApiextensionsV1Api->list_custom_resource_definition: %s\n" % e)
      