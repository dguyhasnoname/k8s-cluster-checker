import modules.message
import threading as threading
import sys, time, os, getopt, argparse, re
import pandas as pd
import xlsxwriter
import glob
start_time = time.time()
from modules import process as k8s

class Logger(object):
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass

sys.stdout = Logger("./report")

class Cluster:
    # fetching cluster name from modules/get_cm.py
    def get_cluster_name():
        from modules.get_cm import K8sConfigMap
        cm = K8sConfigMap.get_cm('kube-system')
        for item in cm.items:
            if 'kubeadm-config' in item.metadata.name:
                if 'clusterName' in item.data['ClusterConfiguration']:
                    cluster_name = re.search(r"clusterName: ([\s\S]+)controlPlaneEndpoint", \
                    item.data['ClusterConfiguration']).group(1)
                    print (k8s.Output.BOLD + "\nCluster name: "+ \
                    k8s.Output.RESET + "{}".format(cluster_name))
            else:
                pass
        return cluster_name

    global cluster_name
    cluster_name = get_cluster_name()

    # fetching nodes data from nodes.py
    def get_node_data(v):
        import nodes as node
        print ("\nNode details:")
        node._Nodes.get_nodes_details(v)
    
    # getting namespaced data
    def get_namespaced_data(v):
        # fetching namespaced data from namespace.py
        import namespace as ns
        data = ns.Namespace.get_ns_data(False,'')

        # variables to store data from get_ns_data function from namespace.py
        cluster_pods_list, cluster_svc_list = data[1], data[2]

        # analysing security context from security_context function in modules/process.py
        k8s.Check.security_context('pods', cluster_pods_list, \
        ['NAMESPACE', 'POD', 'CONTAINER_NAME', 'PRIVILEGED_ESC', \
        'PRIVILEGED', 'READ_ONLY_FS', 'RUN_AS_NON_ROOT', 'RUNA_AS_USER'], \
        v, 'all')

        # analysing health checks from health_probes function in modules/process.py
        k8s.Check.health_probes('pods', cluster_pods_list, \
        ['NAMESPACE', 'POD', 'CONTAINER_NAME', 'READINESS_PROPBE', 'LIVENESS_PROBE'], \
        v, 'all')

        # analysing limit/requests from resources function in modules/process.py
        k8s.Check.resources('pods',cluster_pods_list, \
        ['NAMESPACE', 'POD', 'CONTAINER_NAME', 'LIMITS', 'REQUESTS'], v, 'all')

        # analysing qos context from qos function in modules/process.py
        k8s.Check.qos('pods', cluster_pods_list, ['NAMESPACE', 'POD', 'QoS'], \
        v, 'all')

        # analysing image_pull_policy from image_pull_policy function in modules/process.py
        k8s.Check.image_pull_policy('pods', cluster_pods_list, \
        ['DEPLOYMENT', 'CONTAINER_NAME', 'IMAGE', 'IMAGE_PULL_POLICY'], \
        v, 'all')

        # analysing services from get_service function in modules/process.py
        k8s.Service.get_service('services', cluster_svc_list, \
        ['NAMESPACE', 'SERVICE', 'SERVICE_TYPE', 'CLUSTER_IP', 'SELECTOR'], \
        v, 'all')

    # fetching control plane data from control_plane.py
    def get_ctrl_plane_data(v):
        import control_plane as cp
        print ("\nControl plane details:")
        cp.CtrlPlane.get_ctrl_plane_pods()
        cp.CtrlPlane.check_ctrl_plane_pods_properties(v)
    
    # fetching RBAC data from rbac.py
    def get_rbac_details(v):
        import rbac as rbac
        print ("\nRBAC details:")
        rbac.call_all(v,'')

    # fetching CRD data from crds.py
    def get_crd_details(v):
        import crds as crds
        print ("\nCRD details:")
        crds.call_all(v,'')

    # generating combined report for the cluster
    def merge_reports():
        combined_report_file = './reports/combined_cluster_report.xlsx'
        csv_report_folder = '/reports/csv'
        writer = pd.ExcelWriter(combined_report_file, engine='xlsxwriter')
        csv_list = next(os.walk('.' + csv_report_folder))[2]
        csv_list.sort()
        for host in csv_list:
            path = os.path.join(os.getcwd() + csv_report_folder, host)
            for f in glob.glob(path):
                df = pd.read_csv(f)
                df.to_excel(writer, sheet_name=os.path.basename(f)[:31])
        writer.save()
        print ("[INFO] {} reports generated for cluster {}"\
        .format(len(csv_list), cluster_name))
        print ("[INFO] Combined cluster report file: {}"\
        .format(combined_report_file))             

def call_all(v):  
    k8s.Output.separator(k8s.Output.GREEN,u'\u2581')
    Cluster.get_node_data(v)
    k8s.Output.separator(k8s.Output.GREEN,u'\u2581')
    Cluster.get_ctrl_plane_data(v)
    k8s.Output.separator(k8s.Output.GREEN,u'\u2581')
    Cluster.get_namespaced_data(v)
    k8s.Output.separator(k8s.Output.GREEN,u'\u2581')
    Cluster.get_crd_details(v)
    k8s.Output.separator(k8s.Output.GREEN,u'\u2581')
    Cluster.get_rbac_details(v)
    k8s.Output.separator(k8s.Output.GREEN,u'\u2581')
    Cluster.merge_reports()

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], \
        "hvr", ["help", "verbose", "report"])
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
        print(k8s.Output.RED + "[ERROR] " \
        + k8s.Output.RESET + 'Interrupted from keyboard!')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)