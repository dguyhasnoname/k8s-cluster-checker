from kubernetes import client, config
from kubernetes.client.rest import ApiException

config.load_kube_config()
rbac = client.RbacAuthorizationV1Api()

class K8sClusterRole:
    def list_cluster_role():
        print ("\n[INFO] Fetching clusterRoles data...")
        try:
            cluster_roles = rbac.list_cluster_role(timeout_seconds=10)
            return cluster_roles
        except ApiException as e:
            print("Exception when calling RbacAuthorizationV1Api->list_cluster_role: %s\n" % e)

class K8sClusterRoleBinding:
    def list_cluster_role_binding():
        print ("\n[INFO] Fetching clusterRoleBindings data...")
        try:
            cluster_role_bindings = rbac.list_cluster_role_binding(timeout_seconds=10)
            return cluster_role_bindings
        except ApiException as e:
            print("Exception when calling RbacAuthorizationV1Api->list_cluster_role_binding: %s\n" % e)

class K8sNameSpaceRole:
    def list_namespaced_role(ns):
        try:
            if ns != 'all':
                print ("\n[INFO] Fetching {} namespace roles data...".format(ns))
                namespace = ns
                roles = rbac.list_namespaced_role(namespace, timeout_seconds=10)
            else:
                print ("\n[INFO] Fetching all namespace roles data...")  
                roles = rbac.list_role_for_all_namespaces(timeout_seconds=10)
            return roles
        except ApiException as e:
            print("Exception when calling RbacAuthorizationV1Api->list_namespaced_role: %s\n" % e)

class K8sNameSpaceRoleBinding:
    def list_namespaced_role_binding(ns):
        try:
            if ns != 'all':
                print ("\n[INFO] Fetching {} namespace rolebindings data...".format(ns)) 
                namespace = ns
                role_bindings = rbac.list_namespaced_role_binding(namespace, timeout_seconds=10)
            else:
                print ("\n[INFO] Fetching all namespace roleBindings data...")
                role_bindings = rbac.list_role_binding_for_all_namespaces(timeout_seconds=10)
            return role_bindings
        except ApiException as e:
            print("Exception when calling RbacAuthorizationV1Api->list_namespaced_role_binding: %s\n" % e)


