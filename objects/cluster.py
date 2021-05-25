import threading as threading
import sys, time, os, argparse, re
import pandas as pd
import xlsxwriter, glob
start_time = time.time()
from modules.main import GetOpts
from modules.logging import Logger
from modules.output import Output
from modules import process as k8s
from modules.load_kube_config import kubeConfig

kubeConfig.load_kube_config()

class Cluster:
    def __init__(self, cluster_name, logger):
        self.cluster_name = cluster_name
        self.logger = logger

    def get_cluster_name(self):
        from modules.get_cm import K8sConfigMap
        cm = K8sConfigMap.get_cm('kube-system', self.logger)
        for item in cm.items:
            if 'kubeadm-config' in item.metadata.name:
                if 'clusterName' in item.data['ClusterConfiguration']:
                    self.cluster_name = re.search(r"clusterName: ([\s\S]+)controlPlaneEndpoint", \
                    item.data['ClusterConfiguration']).group(1)
                    print (k8s.Output.BOLD + "\nCluster name: "+ \
                    k8s.Output.RESET + "{}".format(self.cluster_name))
                    return self.cluster_name
            else:
                pass

    # fetching nodes data from nodes.py
    def get_node_data(self, v, l):
        import nodes as node
        nodes = node._Nodes(self.logger)
        nodes.get_nodes_details(v, l)

    # fetching control plane data from control_plane.py
    def get_ctrl_plane_data(self, v, l):
        import control_plane as cp
        print ("\nControl plane details:")
        ctrl_plane = cp.CtrlPlane(self.logger)
        ctrl_plane.get_ctrl_plane_pods(l)
        ctrl_plane.check_ctrl_plane_pods_properties(v, l)
            
    # getting namespaced data
    def get_namespaced_data(self, v, l):
        # fetching namespaced data from namespace.py
        import namespace as namespace
        ns = namespace.Namespace(self.logger)
        data = ns.get_ns_data(False, '', l)

        # variables to store data from get_ns_data function from namespace.py
        cluster_pods_list, cluster_svc_list = data[1], data[2]

        # analysing security context from security_context function in modules/process.py
        data_security_context = k8s.Check.security_context('pods', cluster_pods_list, \
        ['NAMESPACE', 'POD', 'CONTAINER_NAME', 'PRIVILEGED_ESC', \
        'PRIVILEGED', 'READ_ONLY_FS', 'RUN_AS_NON_ROOT', 'RUNA_AS_USER'], \
        v, 'all', l, self.logger)
        if l: self.logger.info(data_security_context)

        # analysing health checks from health_probes function in modules/process.py
        data_health_probes = k8s.Check.health_probes('pods', cluster_pods_list, \
        ['NAMESPACE', 'POD', 'CONTAINER_NAME', 'READINESS_PROPBE', 'LIVENESS_PROBE'], \
        v, 'all', l, self.logger)
        if l: self.logger.info(data_health_probes)

        # analysing limit/requests from resources function in modules/process.py
        data_resources = k8s.Check.resources('pods',cluster_pods_list, \
        ['NAMESPACE', 'POD', 'CONTAINER_NAME', 'LIMITS', 'REQUESTS'], v, 'all', l, self.logger)
        if l: self.logger.info(data_resources, self.logger)

        # analysing qos context from qos function in modules/process.py
        data_qos = k8s.Check.qos('pods', cluster_pods_list, ['NAMESPACE', 'POD', 'QoS'], \
        v, 'all', l, self.logger)
        if l: self.logger.info(data_qos)

        # analysing image_pull_policy from image_pull_policy function in modules/process.py
        data_image_pull_policy = k8s.Check.image_pull_policy('pods', cluster_pods_list, \
        ['DEPLOYMENT', 'CONTAINER_NAME', 'IMAGE', 'IMAGE_PULL_POLICY'], \
        v, 'all', l, self.logger)
        if l: self.logger.info(data_image_pull_policy)

        # analysing services from get_service function in modules/process.py
        data_get_service = k8s.Service.get_service('services', cluster_svc_list, \
        ['NAMESPACE', 'SERVICE', 'SERVICE_TYPE', 'IP', 'SELECTOR'], \
        v, 'all', l, self.logger)
        if l: self.logger.info(data_get_service[0])


    # fetching RBAC data from rbac.py
    def get_rbac_details(self, v, l):
        import rbac as rbac
        print ("\nRBAC details:")
        rbac.call_all(v, '', l, self.logger)

    # fetching CRD data from crds.py
    def get_crd_details(self, v, l):
        import crds as crds
        print ("\nCRD details:")
        crds.call_all(v, '', l, self.logger)

    # generating combined report for the cluster
    def merge_reports(self):
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
        writer.handles = None

        print ("{} reports generated for cluster {}".format(len(csv_list), self.cluster_name))
        print ("Combined cluster report file: {}".format(combined_report_file))             

def usage():
    parser=argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""This script can be used to fetch details about any k8s cluster.

Before running script export KUBECONFIG file as env:
    export KUBECONFIG=<kubeconfig file location>

    e.g. export KUBECONFIG=/Users/dguyhasnoname/kubeconfig\n""",
        epilog="""All's well that ends well.""")

    parser.add_argument('-v', '--verbose', action="store_true", help="verbose mode. \
Use this flag to get namespaced pod level config details.")
    parser.add_argument('-l', '--logging', action="store_true", help="Use this \
flag to generate logs in json format")
    parser.add_argument('-f', '--format', action="store_true", help="Use this \
flag to generate output in given format. csv|json. Default is table format.")
    parser.add_argument('-s', '--silent', action="store_true", help="Use this \
flag to silence the logging. Get only proccessed output.")
    args=parser.parse_args()

def call_all(v, l, logger):
    call = Cluster('', logger)
    call.get_cluster_name()
    k8s.Output.separator(k8s.Output.GREEN,u'\u2581', l)
    call.get_node_data(v, l)
    k8s.Output.separator(k8s.Output.GREEN,u'\u2581', l)
    call.get_ctrl_plane_data(v, l)
    k8s.Output.separator(k8s.Output.GREEN,u'\u2581', l)
    call.get_namespaced_data(v,l)
    k8s.Output.separator(k8s.Output.GREEN,u'\u2581', l)
    call.get_crd_details(v, l)
    k8s.Output.separator(k8s.Output.GREEN,u'\u2581', l)
    call.get_rbac_details(v, l)
    k8s.Output.separator(k8s.Output.GREEN,u'\u2581', l)
    call.merge_reports()

def main():
    options = GetOpts.get_opts()
    logger = Logger.get_logger(options[4], options[5])
    if options[0]:
        usage()
    if options:
        call_all(options[1], options[3], logger)
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