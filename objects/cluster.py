from kubernetes import client, config
from kubernetes.client.rest import ApiException
import sys, time, os, getopt, argparse
import datetime
import objects as k8s
import deployments as deploy
import daemonsets as ds
import statefulsets as sts
import pods as pods
import namespace as ns

start_time = time.time()
config.load_kube_config()
core = client.CoreV1Api()

class Cluster:
    def get_all_pods(v):
        all_pod_list = pods.Pods.get_namespaced_pod_list(v)
    
    def get_namespaced_data(v):
        ns.Namespace.get_ns_data(v)

def call_all(v):
    #Cluster.get_all_pods(v)
    Cluster.get_namespaced_data(v)

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hv", ["help", "verbose"])
        if not opts:        
            call_all("")
            
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)
        return

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-v", "--verbose"):
            verbose= True
            call_all(verbose)
        else:
            assert False, "unhandled option"

    print(k8s.Output.GREEN + "\nTotal time taken: " + k8s.Output.RESET + \
    "{}s".format(round((time.time() - start_time), 2)))     

if __name__ == "__main__":
    main()