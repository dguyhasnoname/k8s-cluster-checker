from kubernetes import client, config
from kubernetes.client.rest import ApiException
import sys, time, os, getopt, argparse
start_time = time.time()
import objects as k8s
import namespace as ns
import nodes as node
import control_plane as cp

config.load_kube_config()
core = client.CoreV1Api()

class Cluster:
    def get_node_data(v):
        print ("Node details:")
        node._Nodes.get_nodes_details(v)
    
    def get_namespaced_data(v):
        print ("Namespace details:")
        ns.Namespace.get_ns_data(v)

    def get_ctrl_plane_data(v):
        print ("Control plane details:")
        cp.CtrlPlane.check_ctrl_plane_pods_properties(v)

def call_all(v):
    #Cluster.get_all_pods(v)
    Cluster.get_node_data(v)
    Cluster.get_namespaced_data(v)
    Cluster.get_ctrl_plane_data(v)

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
    try:
        main()
    except KeyboardInterrupt:
        print(k8s.Output.RED + "[ERROR] " + k8s.Output.RESET + 'Interrupted from keyboard!')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)