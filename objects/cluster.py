import modules.message
import sys, time, os, getopt, argparse, re
start_time = time.time()
import objects as k8s
import control_plane as cp
import nodes as node
import rbac as rbac
import namespace as ns
import services as svc
from modules.get_cm import K8sConfigMap

class Cluster:
    def get_cluster_name():
        cm = K8sConfigMap.get_cm('kube-system')
        for item in cm.items:
            if 'kubeadm-config' in item.metadata.name:
                if 'clusterName' in item.data['ClusterConfiguration']:
                    cluster_name = re.search(r"clusterName: ([\s\S]+)controlPlaneEndpoint", \
                    item.data['ClusterConfiguration']).group(1)
                    print (k8s.Output.BOLD + "\nCluster name: "+ k8s.Output.RESET + "{}".format(cluster_name))
            else:
                pass

    def get_node_data(v):
        print ("\nNode details:")
        node._Nodes.get_nodes_details(v)
    
    def get_namespaced_data(v):
        data = ns.Namespace.get_ns_data(False,'')
        cluster_pods_list, cluster_svc_list = data[1], data[2]
        k8s.Check.security_context('pods',cluster_pods_list)
        k8s.Check.health_probes('pods',cluster_pods_list)
        k8s.Check.resources('pods',cluster_pods_list)
        k8s.Check.qos('pods',cluster_pods_list)
        k8s.Check.image_pull_policy('pods',cluster_pods_list)
        k8s.Service.check_service('services', cluster_svc_list)

    def get_ctrl_plane_data(v):
        print ("\nControl plane details:")
        cp.CtrlPlane.get_ctrl_plane_pods()
        cp.CtrlPlane.check_ctrl_plane_pods_properties(v)
    
    def get_rbac_details(v):
        print ("\nRBAC details:")
        rbac.call_all(v,'')

def call_all(v):
    k8s.Output.separator(k8s.Output.GREEN,u'\u2581')
    Cluster.get_cluster_name()
    Cluster.get_node_data(v)
    k8s.Output.separator(k8s.Output.GREEN,u'\u2581')
    Cluster.get_ctrl_plane_data(v)
    k8s.Output.separator(k8s.Output.GREEN,u'\u2581')    
    Cluster.get_namespaced_data(v)
    k8s.Output.separator(k8s.Output.GREEN,u'\u2581')
    Cluster.get_rbac_details(v)
    k8s.Output.separator(k8s.Output.GREEN,u'\u2581')

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
            verbose= True
            call_all(verbose)
        else:
            assert False, "unhandled option"

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