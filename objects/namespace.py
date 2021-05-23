import time, os, argparse, json, sys
from concurrent.futures import ThreadPoolExecutor
start_time = time.time()
from modules.main import GetOpts
from modules import process as k8s
from modules.logging import Logger
from modules.get_pods import K8sPods
from modules.get_svc import K8sService
from modules.get_deploy import K8sDeploy
from modules.get_ds import K8sDaemonSet
from modules.get_sts import K8sStatefulSet
from modules.get_ns import K8sNameSpace
from modules.get_ingress import K8sIngress
from modules.get_jobs import K8sJobs
from modules.get_svc import K8sService
from modules.get_rbac import K8sNameSpaceRole, K8sNameSpaceRoleBinding

class Namespace:
    def __init__(self, logger):
        self.logger = logger
        self.all_ns_list = K8sNameSpace.get_ns(self.logger)

    def get_object_data(self, fun, k8s_object, ns, v, l):
        k8s_object_list = fun
        if len(k8s_object_list.items):
            if not 'services' in k8s_object:
                k8s.Check.security_context(k8s_object, k8s_object_list, \
                ['NAMESPACE', 'POD', 'CONTAINER_NAME', 'PRIVILEGED_ESC', \
                'PRIVILEGED', 'READ_ONLY_FS', 'RUN_AS_NON_ROOT', \
                'RUNA_AS_USER'], v, ns, l, self.logger)

                k8s.Check.health_probes(k8s_object, k8s_object_list, \
                ['NAMESPACE', 'POD', 'CONTAINER_NAME', 'READINESS_PROPBE', \
                'LIVENESS_PROBE'], v, ns, l, self.logger)

                k8s.Check.resources(k8s_object, k8s_object_list, \
                ['NAMESPACE', 'POD', 'CONTAINER_NAME', 'LIMITS', 'REQUESTS'], \
                v, ns, l, self.logger)

                if k8s_object in ['deployments','statefulsets']: 
                    k8s.Check.replica(k8s_object +  'ns', k8s_object_list, \
                    ['NAMESPACE', 'DEPLOYMENT', 'REPLICA_COUNT'], v, ns, l, self.logger)
            else:
                k8s.Service.get_service(k8s_object, k8s_object_list, \
                ['NAMESPACE', 'SERVICE', 'SERVICE_TYPE', 'CLUSTER_IP', \
                'SELECTOR'], v, ns, l, self.logger)
        else:
            self.logger.warning ("No {} found!".format(k8s_object))

    def get_ns_data(self, v, ns, l):
        data, sum_list, empty_ns = [], [], []
        if not ns:
            ns = 'all'
            ns_list = self.all_ns_list
        else:
            ns_list = ns

        # getting objects list in threads
        with ThreadPoolExecutor(max_workers=10) as executor:
            temp_deploy = executor.submit(K8sDeploy.get_deployments, ns, self.logger)
            temp_ds = executor.submit(K8sDaemonSet.get_damemonsets, ns, self.logger)
            temp_sts = executor.submit(K8sStatefulSet.get_sts, ns, self.logger)
            temp_pods = executor.submit(K8sPods.get_pods, ns, self.logger)
            temp_svc = executor.submit(K8sService.get_svc, ns, self.logger)
            temp_ingress = executor.submit(K8sIngress.get_ingress, ns, self.logger)
            temp_jobs = executor.submit(K8sJobs.get_jobs, ns, self.logger)
            temp_role = executor.submit(K8sNameSpaceRole.list_namespaced_role, ns, self.logger)
            temp_role_binding = \
            executor.submit(K8sNameSpaceRoleBinding.list_namespaced_role_binding, ns, self.logger)

        # stroing data from threads ran above
        deployments = temp_deploy.result()
        ds = temp_ds.result()
        sts = temp_sts.result()
        pods = temp_pods.result()
        svc = temp_svc.result()
        ingress = temp_ingress.result()
        jobs = temp_jobs.result()
        roles = temp_role.result()
        role_bindings = temp_role_binding.result()

        # getting count of each ns objects and printing in table
        print ("\n{} namespace details:".format(ns))
        data = k8s.NameSpace.get_ns_details(ns_list, deployments, ds, sts, \
        pods, svc, ingress, jobs, roles, role_bindings)

        # getting total object-wise count across the cluster
        total_ns, total_deploy, total_ds, total_sts, total_pods,  total_svc, \
        total_ing , total_jobs, total_roles, total_role_bindings \
        = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        for i in data:
            total_ns += 1
            total_deploy = total_deploy + i[1]
            total_ds = total_ds + i[2]
            total_sts = total_sts + i[3]
            total_pods = total_pods + i[4]
            total_svc = total_svc + i[5]
            total_ing = total_ing + i[6]
            total_jobs = total_jobs + i[7]
            total_roles = total_roles + i[8]
            total_role_bindings = total_role_bindings + i[9]

            if i[1] == 0 and i[2] == 0 and i[3] == 0 and i[4] == 0 and \
            not i[0] in ['default', 'kube-node-lease', 'kube-public', 'local']:
                empty_ns.append([i[0]])

        # calculating cluster-wide count of objects if namespace is no provided
        if type(ns_list) != str:
            data = k8s.Output.append_hyphen(data, '--------')
            data.append(["Total: " + str(total_ns), total_deploy, total_ds, 
            total_sts, total_pods, total_svc, total_ing, total_jobs, \
            total_roles, total_role_bindings ])
                    
        headers = ['NAMESPACE', 'DEPLOYMENTS', 'DAEMONSETS', 'STATEFULSETS', \
        'PODS', 'SERVICE', 'INGRESS', 'JOBS', 'ROLES', 'ROLE_BINDINGS'] 
        k8s.Output.print_table(data, headers, True, l)

        analysis = {"namespace_namespace_property": "namespace_object_count",
                    "total_namespaces": total_ns,
                    "total_deployments": total_deploy,
                    "total_daemonsets": total_ds,
                    "total_statefulsets": total_sts,
                    "total_servcies": total_svc,
                    "total_ingresses": total_ing,
                    "total_jobs": total_jobs,
                    "total_roles": total_roles,
                    "total_rolebindings": total_role_bindings}

        json_data_all_ns_detail = k8s.Output.json_out(data[:-2], analysis, headers, 'namespace', 'namespace_details', '')  
        if l: self.logger.info(json_data_all_ns_detail)      

        # get namespace wise object details. Will give output in verbose mode
        def get_all_object_data(self, ns, v, l):
            print (k8s.Output.BOLD + "\nNamespace: " + \
            k8s.Output.RESET  + "{}".format(ns))

            Namespace.get_object_data(self, K8sDeploy.get_deployments(ns, self.logger), \
            'deployments', ns, v, l)
            Namespace.get_object_data(self, K8sDaemonSet.get_damemonsets(ns, self.logger), \
            'damemonsets', ns, v, l)
            Namespace.get_object_data(self, K8sStatefulSet.get_sts(ns, self.logger), \
            'statefulsets', ns, v, l)
            Namespace.get_object_data(self, K8sJobs.get_jobs(ns, self.logger), \
            'jobs', ns, v, l)
            Namespace.get_object_data(self, K8sService.get_svc(ns, self.logger), \
            'services', ns, v, l)

        if v:
            if type(ns_list) != str:
                for item in ns_list.items:
                    ns = item.metadata.name
                    k8s.Output.separator(k8s.Output.GREEN, '-', l)
                    get_all_object_data(self, ns, True, l)
            else:
                get_all_object_data(self, ns, v, l)

        # getting namespaces which are empty
        if len(empty_ns) > 0:
            k8s.Output.separator(k8s.Output.GREEN, '-', l)
            print (k8s.Output.YELLOW + "\n[WARNING] " + k8s.Output.RESET + \
            "Below {} namespaces have no workloads running: "\
            .format(len(empty_ns)))
            k8s.Output.print_table(empty_ns, headers, True, l)
            # creating single list of namespace  for  json parsing
            empyt_ns_list = [item for sublist in empty_ns for item in sublist]
            analysis = {"namespace_property": "empty_namespace",
                        "empty_namespace_count": len(empty_ns),
                        "empty_namespace_list": empyt_ns_list
                        }
            
            if l: self.logger.info(json.dumps(analysis))

        return [ data , pods, svc, deployments, ds, jobs, ingress ]

def usage():
    parser=argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""This script can be used to fetch details about namespaces in k8s cluster.

Before running script export KUBECONFIG file as env:
    export KUBECONFIG=<kubeconfig file location>
    
    e.g. export KUBECONFIG=/Users/dguyhasnoname/kubeconfig\n""",
        epilog="""All's well that ends well.""")
    
    parser.add_argument('-v', '--verbose', action="store_true", help="verbose mode. \
Use this flag to get namespaced pod level config details.")
    parser.add_argument('-n', '--namespace', action="store_true", help="namespace selector. \
Use this flag to get namespaced details. If this flag is not \
used,    is returned")
    parser.add_argument('-l', '--logging', action="store_true", help="namespace selector. \
Use this flag to get namespaced details in JSON format on stdout. If this flag is not \
used, all namespace details is returned")
    args=parser.parse_args()
        
def call_all(v, ns, l, logger):
    call = Namespace(logger)
    call.get_ns_data(v, ns, l)

def main():
    options = GetOpts.get_opts()
    logger = Logger.get_logger(options[4], options[5])
    if options[0]:
        usage()
    if options:
        call_all(options[1], options[2], options[3], logger)
        k8s.Output.time_taken(start_time)       

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(k8s.Output.RED + "[ERROR] " \
        + k8s.Output.RESET + 'Interrupted from keyboard!')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)