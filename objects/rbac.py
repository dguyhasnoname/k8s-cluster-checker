import time, os, argparse, re, sys
from concurrent.futures import ThreadPoolExecutor
start_time = time.time()
from modules.main import GetOpts
from modules import logging as logger
from modules import process as k8s
from modules.get_rbac import K8sClusterRole, K8sClusterRoleBinding, \
K8sNameSpaceRole, K8sNameSpaceRoleBinding

class ClusterRBAC:
    def __init__(self,ns):
        global namespace
        self.ns = ns
        if not ns:
            ns = 'all'
        namespace = ns

        # pulling rbac data in threads for fast execution
        global cluster_role_list, cluster_role_binding_list, ns_role_list, \
        ns_role_binding_list, _logger
        _logger = logger.get_logger('Namespace')
        with ThreadPoolExecutor(max_workers=5) as executor:      
            tmp_cluster_role_list = \
            executor.submit(K8sClusterRole.list_cluster_role)
            tmp_cluster_role_binding_list = \
            executor.submit(K8sClusterRoleBinding.list_cluster_role_binding)
            tmp_ns_role_list = \
            executor.submit(K8sNameSpaceRole.list_namespaced_role, ns)
            tmp_ns_role_binding_list = \
            executor.submit(K8sNameSpaceRoleBinding.list_namespaced_role_binding, ns)

        cluster_role_list = tmp_cluster_role_list.result()
        cluster_role_binding_list = tmp_cluster_role_binding_list.result()
        ns_role_list = tmp_ns_role_list.result()
        ns_role_binding_list = tmp_ns_role_binding_list.result()

    def get_rbac_count(v, l):
        headers = ['CLUSTER_ROLE', 'CLUSTER_ROLE_BINDING', 'ROLE', \
        'ROLE_BINDING']
        k8s.Output.print_table([[len(cluster_role_list.items), \
        len(cluster_role_binding_list.items), len(ns_role_list.items), \
        len(ns_role_binding_list.items)]], headers, True, l) 
       
    def get_cluster_role(v, l):
        k8s_object = "clusterroles"
        data = []
        headers = ['CLUSTER_ROLE', 'RULES', 'API_GROUPS', 'RESOURCES', 'VERBS']
        
        for item in cluster_role_list.items:
            if item.rules:
                rules = k8s.Rbac.get_rules(item.rules)            
                data.append([item.metadata.name, len(item.rules), \
                rules[0], rules[1], rules[2]])
            else:
                data.append([item.metadata.name, "-", "-", "-", "-"])
        k8s.Rbac.analyse_role(data, headers, k8s_object, 'all', l) 
        data = k8s.Output.append_hyphen(data, '-----------')
        data.append(["Total: " + str(len(cluster_role_list.items)), \
        rules[3], "-", "-", "-"])
        k8s.Output.print_table(data, headers, v, l)

    def get_cluster_role_binding(v, l): 
        data, rules_count = [], 0
        headers = ['CLUSTER_ROLE_BINDING', 'CLUSTER_ROLE', \
        'SERVICE_ACCOUNT', 'NAMESPACE']
        
        for item in cluster_role_binding_list.items:
            if item.subjects:
                for i in item.subjects:
                    data.append([item.metadata.name, item.role_ref.name, \
                    i.name, i.namespace])
            else:
                data.append([item.metadata.name, item.role_ref.name, '', ''])
        data = k8s.Output.append_hyphen(data, '-----------')
        data.append(["Total: " + str(len(cluster_role_binding_list.items)), \
        "-", "-", "-"])
        k8s.Output.print_table(data, headers, v, l)
        k8s.Output.csv_out(data, headers, 'rbac', 'cluster_role_binding', 'all')
        json_data = k8s.Output.json_out(data[:-2], '', headers, 'rbac', \
        'cluster_role_binding', 'all')
        if l: _logger.info(json_data)          

    def get_ns_role(v, l):    
        data = []
        k8s_object = 'roles'
        headers = ['ROLE', 'NAMESPACE', 'RULES', 'API_GROUPS', 'RESOURCES', 'VERBS']
        for item in ns_role_list.items:
            if item.rules:
                rules = k8s.Rbac.get_rules(item.rules)
                data.append([item.metadata.name, item.metadata.namespace, \
                len(item.rules), rules[0], rules[1], rules[2]])
            else:
                data.append([item.metadata.name, item.metadata.namespace, \
                "-", "-", "-", "-"])
        k8s.Rbac.analyse_role(data, headers, k8s_object, namespace, l)
        data = k8s.Output.append_hyphen(data, '---------')
        data.append(["Total: " + str(len(ns_role_list.items)), \
        "-", "-", "-",  "-", "-"])          
        k8s.Output.print_table(data, headers, v, l)

    def get_ns_role_binding(v, l):      
        data = []
        headers = ['ROLE_BINDING', 'NAMESPACE', 'ROLE', 'GROUP_BINDING']
        for item in ns_role_binding_list.items:
            if item.subjects:
                subjects = ""
                for i in item.subjects:
                    if len(item.subjects) > 1:
                        subjects = subjects + i.name + '\n'
                    else:
                        subjects = i.name
                data.append([item.metadata.name, item.metadata.namespace, \
                item.role_ref.name, subjects])
            else:
                data.append([item.metadata.name, item.metadata.namespace, \
                item.role_ref.name, 'None'])
        data = k8s.Output.append_hyphen(data, '---------')
        data.append(["Total: " + str(len(ns_role_binding_list.items)), \
        "-", "-", "-"]) 
        k8s.Output.print_table(data, headers, v, l)
        k8s.Output.csv_out(data, headers, 'rbac', 'ns_role_binding', namespace)
        json_data = k8s.Output.json_out(data[:-2], '', headers, 'rbac', \
        'ns_role_binding', namespace)
        if l:  _logger.info(json_data)  

def usage():
    parser=argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""This script can be used to fetch details about rbac \
in k8s cluster.

Before running script export KUBECONFIG file as env:

    export KUBECONFIG=/Users/dguyhasnoname/kubeconfig\n""",
        epilog="""All's well that ends well.""")
    
    parser.add_argument('-v', '--verbose', action="store_true", \
    help="verbose mode. Use this flag to get namespace rbac details.")
    parser.add_argument('-n', '--namespace', action="store_true", help="namespace selector. \
Use this flag to get namespaced rbac details. If this flag is not \
used, all namespace details is returned.")    
    args=parser.parse_args()

def call_all(v, ns, l):
    ClusterRBAC(ns)
    ClusterRBAC.get_rbac_count(v, l)      
    if not ns:
        ClusterRBAC.get_cluster_role(v, l)
        ClusterRBAC.get_cluster_role_binding(v, l)
    ClusterRBAC.get_ns_role(v, l)
    ClusterRBAC.get_ns_role_binding(v, l)

def main():
    options = GetOpts.get_opts()
    if options[0]:
        usage()
    if options:
        call_all(options[1], options[2], options[3])
        k8s.Output.time_taken(start_time)     

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(k8s.Output.RED + "[ERROR] " + \
        k8s.Output.RESET + 'Interrupted from keyboard!')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)