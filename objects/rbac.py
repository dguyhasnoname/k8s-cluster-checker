import time, os, argparse, re, sys
from concurrent.futures import ThreadPoolExecutor
start_time = time.time()
from modules.main import ArgParse
from modules.logging import Logger
from modules import process as k8s
from modules.get_rbac import K8sClusterRole, K8sClusterRoleBinding, K8sNameSpaceRole, K8sNameSpaceRoleBinding

class ClusterRBAC:
    def __init__(self, namespace, logger):
        self.namespace = namespace
        self.logger = logger
        if not self.namespace: self.namespace = 'all'
        # pulling rbac data in threads for fast execution

        with ThreadPoolExecutor(max_workers=5) as executor:      
            tmp_cluster_role_list = \
            executor.submit(K8sClusterRole.list_cluster_role, self.logger)
            tmp_cluster_role_binding_list = \
            executor.submit(K8sClusterRoleBinding.list_cluster_role_binding, self.logger)
            tmp_ns_role_list = \
            executor.submit(K8sNameSpaceRole.list_namespaced_role, self.namespace, self.logger)
            tmp_ns_role_binding_list = \
            executor.submit(K8sNameSpaceRoleBinding.list_namespaced_role_binding, self.namespace, self.logger)

        self.cluster_role_list = tmp_cluster_role_list.result()
        self.cluster_role_binding_list = tmp_cluster_role_binding_list.result()
        self.ns_role_list = tmp_ns_role_list.result()
        self.ns_role_binding_list = tmp_ns_role_binding_list.result()

    def get_rbac_count(self, v, l):
        headers = ['CLUSTER_ROLE', 'CLUSTER_ROLE_BINDING', 'ROLE', \
        'ROLE_BINDING']
        k8s.Output.print_table([[len(self.cluster_role_list.items), \
        len(self.cluster_role_binding_list.items), len(self.ns_role_list.items), \
        len(self.ns_role_binding_list.items)]], headers, True, l) 
       
    def get_cluster_role(self, v, l):
        k8s_object = "clusterroles"
        data = []
        headers = ['CLUSTER_ROLE', 'RULES', 'API_GROUPS', 'RESOURCES', 'VERBS']
        
        for item in self.cluster_role_list.items:
            if item.rules:
                rules = k8s.Rbac.get_rules(item.rules)            
                data.append([item.metadata.name, len(item.rules), \
                rules[0], rules[1], rules[2]])
            else:
                data.append([item.metadata.name, "-", "-", "-", "-"])
        k8s.Rbac.analyse_role(data, headers, k8s_object, 'all', l, self.logger) 
        data = k8s.Output.append_hyphen(data, '-----------')
        data.append(["Total: " + str(len(self.cluster_role_list.items)), \
        rules[3], "-", "-", "-"])
        k8s.Output.print_table(data, headers, v, l)

    def get_cluster_role_binding(self, v, l): 
        data, rules_count = [], 0
        headers = ['CLUSTER_ROLE_BINDING', 'CLUSTER_ROLE', \
        'SERVICE_ACCOUNT', 'NAMESPACE']
        
        for item in self.cluster_role_binding_list.items:
            if item.subjects:
                for i in item.subjects:
                    data.append([item.metadata.name, item.role_ref.name, \
                    i.name, i.namespace])
            else:
                data.append([item.metadata.name, item.role_ref.name, '', ''])
        data = k8s.Output.append_hyphen(data, '-----------')
        data.append(["Total: " + str(len(self.cluster_role_binding_list.items)), \
        "-", "-", "-"])
        k8s.Output.print_table(data, headers, v, l)
        k8s.Output.csv_out(data, headers, 'rbac', 'cluster_role_binding', 'all')
        json_data = k8s.Output.json_out(data[:-2], '', headers, 'rbac', \
        'cluster_role_binding', 'all')
        if l: self.logger.info(json_data)          

    def get_ns_role(self, v, l):    
        data = []
        k8s_object = 'roles'
        headers = ['ROLE', 'NAMESPACE', 'RULES', 'API_GROUPS', 'RESOURCES', 'VERBS']
        for item in self.ns_role_list.items:
            if item.rules:
                rules = k8s.Rbac.get_rules(item.rules)
                data.append([item.metadata.name, item.metadata.namespace, \
                len(item.rules), rules[0], rules[1], rules[2]])
            else:
                data.append([item.metadata.name, item.metadata.namespace, \
                "-", "-", "-", "-"])
        k8s.Rbac.analyse_role(data, headers, k8s_object, self.namespace, l, self.logger)
        data = k8s.Output.append_hyphen(data, '---------')
        data.append(["Total: " + str(len(self.ns_role_list.items)), \
        "-", "-", "-",  "-", "-"])          
        k8s.Output.print_table(data, headers, v, l)

    def get_ns_role_binding(self, v, l):      
        data = []
        headers = ['ROLE_BINDING', 'NAMESPACE', 'ROLE', 'GROUP_BINDING']
        for item in self.ns_role_binding_list.items:
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
        data.append(["Total: " + str(len(self.ns_role_binding_list.items)), \
        "-", "-", "-"]) 
        k8s.Output.print_table(data, headers, v, l)
        k8s.Output.csv_out(data, headers, 'rbac', 'ns_role_binding', self.namespace)
        json_data = k8s.Output.json_out(data[:-2], '', headers, 'rbac', \
        'ns_role_binding', self.namespace)
        if l:  self.logger.info(json_data)

def call_all(v, namespace, l, logger):
    call = ClusterRBAC(namespace, logger)
    call.get_rbac_count(v, l)      
    if not namespace:
        call.get_cluster_role(v, l)
        call.get_cluster_role_binding(v, l)
    call.get_ns_role(v, l)
    call.get_ns_role_binding(v, l)

def main():
    args = ArgParse.arg_parse()
    # args is [u, verbose, ns, l, format, silent]
    logger = Logger.get_logger(args.format, args.silent)
    if args:
        call_all(args.verbose, args.namespace, args.logging, logger)
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