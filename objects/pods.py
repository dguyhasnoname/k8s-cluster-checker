import time, os, argparse, sys
start_time = time.time()
from modules.main import GetOpts
from modules.logging import Logger
from modules import process as k8s
from modules.get_pods import K8sPods

def usage():
    parser=argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""This script can be used to fetch details about pods deployed \
in namespaces in k8s cluster.

Before running script export KUBECONFIG file as env:
    export KUBECONFIG=<kubeconfig file location>
    
    e.g. export KUBECONFIG=/Users/dguyhasnoname/kubeconfig\n""",
        epilog="""All's well that ends well.""")
    
    parser.add_argument('-v', '--verbose', action="store_true", help="verbose mode. \
Use this flag to get namespaced pod level config details.")
    parser.add_argument('-n', '--namespace', help="namespace selector. \
Use this flag to get namespaced pod details. If this flag is not \
used, all namespace details is returned")
    args=parser.parse_args()

class _Pods:
    def __init__(self, namespace, logger):
        self.namespace = namespace
        self.logger = logger
        if not namespace: namespace = 'all'  
        self.k8s_object_list = K8sPods.get_pods(self.namespace, self.logger) 
        self.k8s_object = 'pods'

    def get_namespaced_pod_list(self, v, l):
        data = []
        headers = ['NAMESPACE', 'POD']
        for item in self.k8s_object_list.items:
            data.append([item.metadata.namespace, item.metadata.name])
        if v: print ("Total pods: {}".format(len(data)))            
        k8s.Output.print_table(data, headers, v)
        return json.dumps(data)
    
    def check_pod_security(self, v, l):
        headers = ['NAMESPACE', 'POD', 'CONTAINER_NAME', 'PRIVILEGED_ESC', \
        'PRIVILEGED', 'READ_ONLY_FS', 'RUN_AS_NON_ROOT', 'RUNA_AS_USER']        
        data = k8s.Check.security_context(self.k8s_object, self.k8s_object_list, headers, \
        v, self.namespace, l, self.logger)
        if l: self.logger.info(data)

    def check_pod_health_probes(self, v, l):
        headers = ['NAMESPACE', 'POD', 'CONTAINER_NAME', 'READINESS_PROPBE', \
        'LIVENESS_PROBE']
        data = k8s.Check.health_probes(self.k8s_object, self.k8s_object_list, headers, \
        v, self.namespace, l, self.logger)
        if l: self.logger.info(data)

    def check_pod_resources(self, v, l):
        headers = ['NAMESPACE', 'POD', 'CONTAINER_NAME', 'LIMITS', 'REQUESTS']
        data = k8s.Check.resources(self.k8s_object, self.k8s_object_list, headers, \
        v, self.namespace, l, self.logger)
        if l: self.logger.info(data)

    def check_pod_qos(self, v, l):
        headers = ['NAMESPACE', 'POD', 'QoS']
        data = k8s.Check.qos(self.k8s_object, self.k8s_object_list, headers, \
        v, self.namespace, l, self.logger)
        if l: self.logger.info(data)

    def check_pod_tolerations_affinity_node_selector_priority(self, v, l):
        headers = ['NAMESPACE', 'POD', 'NODE_SELECTOR', 'TOLERATIONS', \
        'AFFINITY', 'PRIORITY_CLASS']
        data = k8s.Check.tolerations_affinity_node_selector_priority(self.k8s_object, \
        self.k8s_object_list, headers, v, self.namespace, l, self.logger)
        if l: self.logger.info(data)

    def check_image_pull_policy(self, v, l):
        headers = ['DEPLOYMENT', 'CONTAINER_NAME', 'IMAGE', 'IMAGE_PULL_POLICY']
        data = k8s.Check.image_pull_policy(self.k8s_object, self.k8s_object_list, headers, \
        v, self.namespace, l, self.logger)
        if l: self.logger.info(data)

def call_all(v, ns, l, logger):
    call = _Pods(ns, logger)
    call.check_pod_security(v, l)
    call.check_pod_health_probes(v, l)
    call.check_pod_resources(v, l)
    call.check_pod_qos(v, l)
    call.check_image_pull_policy(v, l)
    call.check_pod_tolerations_affinity_node_selector_priority(v, l)

def main():
    options = GetOpts.get_opts()
    logger = Logger.get_logger(options[4], options[5])
    if options[0]:
        usage()
    if options:
        call_all(options[1], options[2], options[3], logger)
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