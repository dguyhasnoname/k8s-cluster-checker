from kubernetes import client
from kubernetes.client.rest import ApiException

core = client.CoreV1Api()

class K8sNodes:
    def get_nodes(logger):
        logger.info ("Fetching nodes data...")
        try:
            node_list = core.list_node(timeout_seconds=10)
            return node_list
        except ApiException as e:
            print("Exception when calling CoreV1Api->list_node: %s\n" % e)

    def read_nodes(node):
        print ("\n[INFO] Fetching node {} data...".format(node))
        try:
            name = node
            node_detail = core.read_node(name)
            return node_detail
        except ApiException as e:
            print("Exception when calling CoreV1Api->read_node: %s\n" % e)        