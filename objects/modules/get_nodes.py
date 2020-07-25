from kubernetes import client, config
from kubernetes.client.rest import ApiException

class K8sNodes:
    def get_nodes(core):
        print ("\n[INFO] Fetching nodes data...")
        try:
            node_list = core.list_node(timeout_seconds=10)
            return node_list
        except ApiException as e:
            print("Exception when calling CoreV1Api->list_node: %s\n" % e)