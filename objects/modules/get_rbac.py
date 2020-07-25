from kubernetes.client.rest import ApiException

class K8sClusterRole:
    def list_cluster_role(rbac):
        print ("\n[INFO] Fetching clusterRoles data...")
        try:
            cluster_roles = rbac.list_cluster_role(timeout_seconds=10)
            return cluster_roles
        except ApiException as e:
            print("Exception when calling RbacAuthorizationV1Api->list_cluster_role: %s\n" % e)

class K8sClusterRoleBinding:
    def list_cluster_role_binding(rbac):
        print ("\n[INFO] Fetching clusterRoleBindings data...")
        try:
            cluster_role_bindings = rbac.list_cluster_role_binding(timeout_seconds=10)
            return cluster_role_bindings
        except ApiException as e:
            print("Exception when calling RbacAuthorizationV1Api->list_cluster_role_binding: %s\n" % e)

class K8sNameSpaceRole:
    def list_namespaced_role(ns,rbac):
        print ("\n[INFO] Fetching roles data...")
        try:
            if ns != 'all': 
                namespace = ns
                roles = rbac.list_namespaced_role(namespace, timeout_seconds=10)
            else:
                roles = rbac.list_role_for_all_namespaces(timeout_seconds=10)
            return roles
        except ApiException as e:
            print("Exception when calling RbacAuthorizationV1Api->list_namespaced_role: %s\n" % e)

class K8sNameSpaceRoleBinding:
    def list_namespaced_role_binding(ns,rbac):
        print ("\n[INFO] Fetching roleBindings data...")
        try:
            if ns != 'all': 
                namespace = ns
                role_bindings = rbac.list_namespaced_role_binding(namespace, timeout_seconds=10)
            else:
                role_bindings = rbac.list_role_binding_for_all_namespaces(timeout_seconds=10)
            return role_bindings
        except ApiException as e:
            print("Exception when calling RbacAuthorizationV1Api->list_namespaced_role_binding: %s\n" % e)


