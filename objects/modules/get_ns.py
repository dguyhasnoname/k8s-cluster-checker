from kubernetes import client
from kubernetes.client.rest import ApiException
from .load_kube_config import kubeConfig

kubeConfig.load_kube_config()
core = client.CoreV1Api()

class K8sNameSpace:
    def get_ns():
        print ("\n[INFO] Fetching namespaces data...")
        try:
            ns_list = core.list_namespace(timeout_seconds=10)
            return ns_list
        except ApiException as e:
            print("Exception when calling CoreV1Api->list_namespace: %s\n" % e)