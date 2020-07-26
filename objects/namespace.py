from modules import message
import sys, time, os, getopt, argparse
start_time = time.time()
import objects as k8s
from modules.get_pods import K8sPods
from modules.get_svc import K8sService
from modules.get_deploy import K8sDeploy
from modules.get_ds import K8sDaemonSet
from modules.get_sts import K8sStatefulSet
from modules.get_ns import K8sNameSpace
from modules.get_ingress import K8sIngress
from modules.get_jobs import K8sJobs
from modules.get_svc import K8sService

class Namespace:
    global all_ns_list
    all_ns_list = K8sNameSpace.get_ns()

    # def workload_sharing_data(data):
    #     data = sorted(data, key=lambda x: x[4])[::-1]
    #     highest_pod_count = data[0][4]
    #     print (highest_pod_count)
    #     k8s.Output.bar(highest_pod_count, data[0][1], \
    #     'is running highest workload share','cluster','pods')

    def get_object_data(fun,k8s_object):
        k8s_object_list = fun
        if len(k8s_object_list.items):
            if not 'services' in k8s_object:
                k8s.Check.security_context(k8s_object, k8s_object_list)
                k8s.Check.health_probes(k8s_object, k8s_object_list)
                k8s.Check.resources(k8s_object, k8s_object_list)
                if k8s_object in ['deployments','statefulsets']: k8s.Check.replica(k8s_object, k8s_object_list)
            else:
                k8s.Service.check_service(k8s_object, k8s_object_list)
        else:
            print (k8s.Output.YELLOW  + "[WARNING] " + k8s.Output.RESET + "No {} found!".format(k8s_object))

    def get_ns_data(v,ns):
        data, sum_list, empty_ns = [], [], []
        if not ns:
            ns = 'all'
            ns_list = all_ns_list
        else:
            ns_list = ns
        deployments = K8sDeploy.get_deployments(ns)
        ds = K8sDaemonSet.get_damemonsets(ns)
        sts = K8sStatefulSet.get_sts(ns)
        pods = K8sPods.get_pods(ns)
        svc = K8sService.get_svc(ns)
        ingress = K8sIngress.get_ingress(ns)
        jobs = K8sJobs.get_jobs(ns)

        print ("\n{} Namespace details:".format(ns))
        data = k8s.NameSpace.get_ns_details(ns_list,deployments,ds,sts,pods,svc,ingress,jobs)

        total_ns, total_deploy, total_ds, total_sts, total_pods,  total_svc, \
        total_ing , total_jobs = 0, 0, 0, 0, 0, 0, 0, 0
        for i in data:
            total_ns += 1
            total_deploy = total_deploy + i[1]
            total_ds = total_ds + i[2]
            total_sts = total_sts + i[3]
            total_pods = total_pods + i[4]
            total_svc = total_svc + i[5]
            total_ing = total_ing + i[6]
            total_jobs = total_jobs + i[7]

            if i[1] == 0 and i[2] == 0 and i[3] == 0 and i[4] == 0 and \
            not i[0] in ['default', 'kube-node-lease', 'kube-public', 'local']:
                empty_ns.append([i[0]])

        if type(ns_list) != str:
            data.append(['----------', '---', '---', '---', '---','---', '---', '---'])
            data.append(["Total: " + str(total_ns), total_deploy, total_ds, total_sts, \
            total_pods, total_svc, total_ing, total_jobs])
                    
        headers = ['NAMESPACE', 'DEPLOYMENTS', 'DAEMONSETS', 'STATEFULSETS', 'PODS', 'SERVICE', 'INGRESS', 'JOBS'] 
        k8s.Output.print_table(data,headers,True)

        def get_all_object_data(ns):
            print (k8s.Output.BOLD + "\nNamespace: " + k8s.Output.RESET  + "{}".format(ns))
            Namespace.get_object_data(K8sDeploy.get_deployments(ns),'deployments')
            Namespace.get_object_data(K8sDaemonSet.get_damemonsets(ns),'damemonsets')
            Namespace.get_object_data(K8sStatefulSet.get_sts(ns),'statefulsets')
            Namespace.get_object_data(K8sJobs.get_jobs(ns),'jobs')
            Namespace.get_object_data(K8sService.get_svc(ns),'services')

        if v:
            if type(ns_list) != str:
                for item in ns_list.items:
                    ns = item.metadata.name  
                    get_all_object_data(ns)
            else:
                get_all_object_data(ns)

            if len(empty_ns) > 0:
                print (k8s.Output.YELLOW + "\n[WARNING] " + k8s.Output.RESET + \
                "Below {} namespaces have no workloads running: ".format(len(empty_ns)))
                k8s.Output.print_table(empty_ns,headers,True)
        return [ data , pods]
        
def call_all(v,ns):
    Namespace.get_ns_data(v,ns)
    

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvn:", ["help", "verbose", "namespace"])
        if not opts:        
            call_all("","")
            sys.exit()
            
    except getopt.GetoptError as err:
        print(err)
        return
    verbose, ns = '', ''
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-v", "--verbose"):
            verbose = True
        elif o in ("-n", "--namespace"):
            if not verbose: verbose = False
            ns = a          
        else:
            assert False, "unhandled option"
    call_all(verbose,ns)
    k8s.Output.time_taken(start_time)  

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(k8s.Output.RED + "[ERROR] " + k8s.Output.RESET + 'Interrupted from keyboard!')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)