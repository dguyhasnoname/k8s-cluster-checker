from kubernetes import client, config
from kubernetes.client.rest import ApiException

class K8sNameSpace:
    def get_ns(core):
        try:
            ns_list = core.list_namespace(timeout_seconds=10)
            return ns_list
        except ApiException as e:
            print("Exception when calling CoreV1Api->list_namespace: %s\n" % e)