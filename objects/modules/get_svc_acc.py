from kubernetes import client
from kubernetes.client.rest import ApiException
from .load_kube_config import kubeConfig

kubeConfig.load_kube_config()
core = client.CoreV1Api()

class K8sSvcAcc:
    def get_svc_acc(ns):           
        try:
            if ns != 'all':
                print ("\n[INFO] Fetching {} namespace service account data...".format(ns)) 
                namespace = ns
                sa = core.list_namespaced_service_account(namespace, timeout_seconds=5)
            else:
                print ("\n[INFO] Fetching all namespace service account data...") 
                sa = core.list_service_account_for_all_namespaces(timeout_seconds=5)
            return sa
        except ApiException as e:
            print("Exception when calling CoreV1Api->list_service_account_for_all_namespaces: %s\n" % e)