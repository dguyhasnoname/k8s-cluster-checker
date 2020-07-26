from kubernetes import client, config
from kubernetes.client.rest import ApiException

config.load_kube_config()
core = client.CoreV1Api()

class K8sService:
    def get_svc(ns):
        print ("\n[INFO] Fetching services data...")
        try:
            if ns != 'all': 
                namespace = ns            
                services = core.list_namespaced_service(namespace, timeout_seconds=10)
            else:
                services = core.list_service_for_all_namespaces(timeout_seconds=10)
            return services
        except ApiException as e:
            print("Exception when calling AppsV1Api->list_namespaced_service: %s\n" % e)