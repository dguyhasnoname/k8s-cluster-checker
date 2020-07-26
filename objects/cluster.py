import modules.message
import sys, time, os, getopt, argparse
start_time = time.time()
import objects as k8s
import control_plane as cp
import nodes as node
import namespace as ns
import rbac as rbac

class Cluster:
    def get_node_data(v):
        print ("\nNode details:")
        node._Nodes.get_nodes_details(v)
    
    def get_namespaced_data(v):
        ns.Namespace.get_ns_data(v,'')

    def get_ctrl_plane_data(v):
        print ("\nControl plane details:")
        cp.CtrlPlane.get_ctrl_plane_pods()
        cp.CtrlPlane.check_ctrl_plane_pods_properties(v)
    
    def get_rbac_details(v):
        print ("\nRBAC details:")
        rbac.call_all(v)

def call_all(v):
    Cluster.get_node_data(v)
    k8s.Output.separator(k8s.Output.GREEN,u'\u2581')
    Cluster.get_ctrl_plane_data(v)
    k8s.Output.separator(k8s.Output.GREEN,u'\u2581')    
    Cluster.get_namespaced_data(v)
    k8s.Output.separator(k8s.Output.GREEN,u'\u2581')
    Cluster.get_rbac_details(v)


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