from kubernetes.client.rest import ApiException

class K8sService:
    def get_svc(ns,apps):
        print ("\n[INFO] Fetching services data...")
        try:
            if ns != 'all': 
                namespace = ns            
                statefulsets = apps.list_namespaced_service(namespace, timeout_seconds=10)
            else:
                statefulsets = apps.list_service_for_all_namespaces(timeout_seconds=10)
            return statefulsets
        except ApiException as e:
            print("Exception when calling AppsV1Api->list_namespaced_service: %s\n" % e)