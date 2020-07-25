from kubernetes.client.rest import ApiException

class K8sIngress:
    def get_ingress(ns,networking):           
        try:
            print ("\n[INFO] Fetching ingress data...")
            if ns != 'all': 
                namespace = ns
                ingress = networking.list_namespaced_ingress(namespace, timeout_seconds=10)
            else:             
                ingress = networking.list_ingress_for_all_namespaces(timeout_seconds=10)
            return ingress
        except ApiException as e:
            print("Exception when calling NetworkingV1beta1Api->list_namespaced_ingress: %s\n" % e)
