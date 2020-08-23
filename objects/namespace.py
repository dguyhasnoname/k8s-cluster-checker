import sys, time, os, getopt, argparse
from concurrent.futures import ThreadPoolExecutor
start_time = time.time()
from modules import process as k8s
from modules import logging as logger
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
    global all_ns_list, _logger
    _logger = logger.get_logger('Namespace')
    all_ns_list = K8sNameSpace.get_ns()

    # def workload_sharing_data(data):
    #     data = sorted(data, key=lambda x: x[4])[::-1]
    #     highest_pod_count = data[0][4]
    #     print (highest_pod_count)
    #     k8s.Output.bar(highest_pod_count, data[0][1], \
    #     'is running highest workload share','cluster','pods')

    def get_object_data(fun, k8s_object, ns, v, l):
        k8s_object_list = fun
        if len(k8s_object_list.items):
            if not 'services' in k8s_object:
                k8s.Check.security_context(k8s_object, k8s_object_list, \
                ['NAMESPACE', 'POD', 'CONTAINER_NAME', 'PRIVILEGED_ESC', \
                'PRIVILEGED', 'READ_ONLY_FS', 'RUN_AS_NON_ROOT', \
                'RUNA_AS_USER'], v, ns, l)

                k8s.Check.health_probes(k8s_object, k8s_object_list, \
                ['NAMESPACE', 'POD', 'CONTAINER_NAME', 'READINESS_PROPBE', \
                'LIVENESS_PROBE'], v, ns, l)

                k8s.Check.resources(k8s_object, k8s_object_list, \
                ['NAMESPACE', 'POD', 'CONTAINER_NAME', 'LIMITS', 'REQUESTS'], \
                v, ns, l)

                if k8s_object in ['deployments','statefulsets']: 
                    k8s.Check.replica(k8s_object +  'ns', k8s_object_list, \
                    ['NAMESPACE', 'DEPLOYMENT', 'REPLICA_COUNT'], v, ns, l)
            else:
                k8s.Service.get_service(k8s_object, k8s_object_list, \
                ['NAMESPACE', 'SERVICE', 'SERVICE_TYPE', 'CLUSTER_IP', \
                'SELECTOR'], v, ns, l)
        else:
            print (k8s.Output.YELLOW  + "[WARNING] " + k8s.Output.RESET + \
            "No {} found!".format(k8s_object))

    def get_ns_data(v, ns, l):
        data, sum_list, empty_ns = [], [], []
        if not ns:
            ns = 'all'
            ns_list = all_ns_list
        else:
            ns_list = ns

        # getting objects list in threads
        with ThreadPoolExecutor(max_workers=10) as executor:
            temp_deploy = executor.submit(K8sDeploy.get_deployments, ns)
            temp_ds = executor.submit(K8sDaemonSet.get_damemonsets, ns)
            temp_sts = executor.submit(K8sStatefulSet.get_sts, ns)
            temp_pods = executor.submit(K8sPods.get_pods, ns)
            temp_svc = executor.submit(K8sService.get_svc, ns)
            temp_ingress = executor.submit(K8sIngress.get_ingress, ns)
            temp_jobs = executor.submit(K8sJobs.get_jobs, ns)
            temp_role = executor.submit(K8sNameSpaceRole.list_namespaced_role, ns)
            temp_role_binding = \
            executor.submit(K8sNameSpaceRoleBinding.list_namespaced_role_binding, ns)

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

        json_data_all_ns_detail = k8s.Output.json_out(data, analysis, headers, 'namespace', 'namespace_details', '')  
        if l: _logger.info(json_data_all_ns_detail)      

        # get namespace wise object details. Will give output in verbose mode
        def get_all_object_data(ns, v, l):
            print (k8s.Output.BOLD + "\nNamespace: " + \
            k8s.Output.RESET  + "{}".format(ns))

            Namespace.get_object_data(K8sDeploy.get_deployments(ns), \
            'deployments', ns, v, l)
            Namespace.get_object_data(K8sDaemonSet.get_damemonsets(ns), \
            'damemonsets', ns, v, l)
            Namespace.get_object_data(K8sStatefulSet.get_sts(ns), \
            'statefulsets', ns, v, l)
            Namespace.get_object_data(K8sJobs.get_jobs(ns), \
            'jobs', ns, v, l)
            Namespace.get_object_data(K8sService.get_svc(ns), \
            'services', ns, v, l)

        if v:
            if type(ns_list) != str:
                for item in ns_list.items:
                    ns = item.metadata.name
                    k8s.Output.separator(k8s.Output.GREEN, '-', l)
                    get_all_object_data(ns, True, l)
            else:
                get_all_object_data(ns, v, l)

        # getting namespaces which are empty
        if len(empty_ns) > 0:
            k8s.Output.separator(k8s.Output.GREEN, '-', l)
            print (k8s.Output.YELLOW + "\n[WARNING] " + k8s.Output.RESET + \
            "Below {} namespaces have no workloads running: "\
            .format(len(empty_ns)))
            k8s.Output.print_table(empty_ns, headers, True, l)

            analysis = {"namespace_property": "empty_namespace",
                        "empty_namespace_count": len(empty_ns),
                        "empty_namespae_list": empty_ns
                        }
            
            if l: _logger.info(analysis)

        return [ data , pods, svc, deployments, ds, jobs, ingress ]
        
def call_all(v, ns, l):
    Namespace.get_ns_data(v, ns, l)

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], \
        "hvn:l", ["help", "verbose", "namespace", "logging"])
        if not opts:        
            call_all('','','')
            k8s.Output.time_taken(start_time)
            sys.exit()
            
    except getopt.GetoptError as err:
        print(err)
        return
    verbose, ns, l = '', '', ''
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-v", "--verbose"):
            verbose = True
        elif o in ("-n", "--namespace"):
            if not verbose: verbose = False
            ns = a
        elif o in ("-l", "--logging"):
            l = True                      
        else:
            assert False, "unhandled option"
    call_all(verbose, ns, l)
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