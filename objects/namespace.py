from modules import message
from kubernetes import client, config
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


config.load_kube_config()
core = client.CoreV1Api()
apps = client.AppsV1Api()
networking = client.NetworkingV1beta1Api()

class Namespace:
    global all_ns_list
    all_ns_list = K8sNameSpace.get_ns(core)

    # def workload_sharing_data(data):
    #     data = sorted(data, key=lambda x: x[4])[::-1]
    #     highest_pod_count = data[0][4]
    #     print (highest_pod_count)
    #     k8s.Output.bar(highest_pod_count, data[0][1], \
    #     'is running highest workload share','cluster','pods')

    def get_object_data(fun,k8s_object):
        k8s_object_list = fun
        if len(k8s_object_list.items):
            k8s.Check.security_context(k8s_object, k8s_object_list)
            k8s.Check.health_probes(k8s_object, k8s_object_list)
            k8s.Check.resources(k8s_object, k8s_object_list)
            if not 'damemonsets' in k8s_object: k8s.Check.replica(k8s_object, k8s_object_list)
        else:
            print (k8s.Output.YELLOW  + "[WARNING] " + k8s.Output.RESET + "No {} found!".format(k8s_object))

    def get_ns_data(v):
        data, sum_list, empty_ns = [], [], []
        all_deployments = K8sDeploy.get_deployments('all',apps)
        all_ds = K8sDaemonSet.get_damemonsets('all',apps)
        all_sts = K8sStatefulSet.get_sts('all',apps)
        all_pods = K8sPods.get_pods('all',core)
        all_svc = K8sService.get_svc('all',core)
        all_ingress = K8sIngress.get_ingress('all',networking)

        print ("\n\nNamespace details:")
        data = k8s.NameSpace.get_ns_details(all_ns_list,all_deployments,all_ds,all_sts,all_pods,all_svc,all_ingress)

        total_ns, total_deploy, total_ds, total_sts, total_pods,  total_svc, total_ing = 0, 0, 0, 0, 0, 0, 0
        for i in data:
            total_ns += 1
            total_deploy = total_deploy + i[1]
            total_ds = total_ds + i[2]
            total_sts = total_sts + i[3]
            total_pods = total_pods + i[4]
            total_svc = total_svc + i[5]
            total_ing = total_ing + i[6]

            if i[1] == 0 and i[2] == 0 and i[3] == 0 and i[4] == 0 and \
            not i[0] in ['default', 'kube-node-lease', 'kube-public', 'local']:
                empty_ns.append([i[0]])

        data.append(['----------', '---', '---', '---', '---','---', '---'])
        data.append(["Total: " + str(total_ns), total_deploy, total_ds, total_sts, total_pods, total_svc, total_ing])
                    
        headers = ['NAMESPACE', 'DEPLOYMENTS', 'DAEMONSETS', 'STATEFULSETS', 'PODS', 'SERVICE', 'INGRESS'] 
        k8s.Output.print_table(data,headers,True)

        if v:
            for item in all_ns_list.items:
                ns = item.metadata.name  
                print (k8s.Output.BOLD + "\n\nNamespace: " + k8s.Output.RESET  + "{}".format(ns))
                Namespace.get_object_data(K8sDeploy.get_deployments(ns,apps),'deployments')
                Namespace.get_object_data(K8sDaemonSet.get_damemonsets(ns,apps),'damemonsets')
                Namespace.get_object_data(K8sStatefulSet.get_sts(ns,apps),'statefulsets')

            if len(empty_ns) > 0:
                print (k8s.Output.YELLOW + "\n\n[WARNING] " + k8s.Output.RESET + "Below {} namespaces have no workloads running: ".format(len(empty_ns)))
                k8s.Output.print_table(empty_ns,headers,True)
        return data
        
def call_all(v):
    Namespace.get_ns_data(v)

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hv", ["help", "verbose"])
        if not opts:        
            call_all("")
            
    except getopt.GetoptError as err:
        print(err)
        return

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-v", "--verbose"):
            verbose = True
            call_all(verbose)
        else:
            assert False, "unhandled option"

    print(k8s.Output.GREEN + "\nTotal time taken: " + k8s.Output.RESET + \
    "{}s".format(round((time.time() - start_time), 2)))     

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(k8s.Output.RED + "[ERROR] " + k8s.Output.RESET + 'Interrupted from keyboard!')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)