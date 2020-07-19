from kubernetes import client, config
from kubernetes.client.rest import ApiException
import sys, time, os, getopt, argparse
import datetime
import objects as k8s
import deployments as deploy
import daemonsets as ds
import statefulsets as sts
import pods as pods 

start_time = time.time()
config.load_kube_config()
core = client.CoreV1Api()

class K8s:
    def get_ns():
        try:
            ns_list = core.list_namespace(timeout_seconds=10)
            return ns_list
        except ApiException as e:
            print("Exception when calling CoreV1Api->list_namespace: %s\n" % e)

class Namespace:
    global all_ns_list
    all_ns_list = K8s.get_ns()

    def get_ns_list():
        data = []
        for item in all_ns_list.items:
            data.append(item.metadata.name)
        return data

    def get_ns_count(v):
        print ("Total Namespaces: {}".format(len(all_ns_list.items)))
        return len(all_ns_list.items)

    # def workload_sharing_data(data):
    #     data = sorted(data, key=lambda x: x[4])[::-1]
    #     highest_pod_count = data[0][4]
    #     print (highest_pod_count)
    #     k8s.Output.bar(highest_pod_count, data[0][1], \
    #     'is running highest workload share','cluster','pods')

    def get_object_data(fun,k8s_object):
        k8s_object_list = fun
        if len(k8s_object_list.items):
            print (k8s.Output.YELLOW  + "\n[INFO] checking {}...".format(k8s_object) + k8s.Output.RESET)
            k8s.Check.security_context(k8s_object, k8s_object_list)
            k8s.Check.health_probes(k8s_object, k8s_object_list)
            k8s.Check.resources(k8s_object, k8s_object_list)
            if not 'damemonsets' in k8s_object: k8s.Check.replica(k8s_object, k8s_object_list)
        else:
            print (k8s.Output.RED  + "\n[WARNING] " + k8s.Output.RESET + "No {} found!".format(k8s_object))

    def get_ns_data(v):
        data = []
        for item in all_ns_list.items:
            ns = item.metadata.name
                       
            if v:
                print (k8s.Output.BOLD + "\n\nNamespace: " + k8s.Output.RESET  + "{}".format(ns))
                Namespace.get_object_data(deploy.K8s.get_deployments(ns),'deployments')
                Namespace.get_object_data(ds.K8s.get_damemonsets(ns),'damemonsets')
                Namespace.get_object_data(sts.K8s.get_sts(ns),'statefulsets')
                for i in range(120):
                    print (k8s.Output.GREEN + u'\u2581', end="" + k8s.Output.RESET )

            deployment_count = len(deploy.K8s.get_deployments(ns).items)
            ds_count = len(ds.K8s.get_damemonsets(ns).items)
            sts_count = len(sts.K8s.get_sts(ns).items)
            pod_count = len(pods.K8s.get_pods(ns).items)
            data.append([ns, deployment_count, ds_count, sts_count, pod_count])
        headers = ['NAMESPACE', 'DEPLOYMENTS', 'DAEMONSETS', 'STATEFULSETS', 'PODS']                 
        k8s.Output.print_table(data,headers,True)

def call_all(v):
    #Namespace.get_ns_count(v)
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
    main()