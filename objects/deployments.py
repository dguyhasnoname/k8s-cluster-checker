import os, time, json, argparse, sys
from time import sleep
start_time = time.time()
from modules.main import GetOpts
from modules.logging import Logger
from modules import process as k8s
from modules.get_deploy import K8sDeploy

def usage():
    parser=argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""This script can be used to fetch details about deployments \
in k8s cluster.

Before running script export KUBECONFIG file as env:

    export KUBECONFIG=/Users/dguyhasnoname/kubeconfig\n""",
        epilog="""All's well that ends well.""")
    
    parser.add_argument('-v', '--verbose', action="store_true", \
    help="verbose mode. Use this flag to get namespace deployment details.")
    parser.add_argument('-n', '--namespace', action="store_true", help="namespace selector. \
Use this flag to get namespaced deployments details. If this flag is not \
used, all namespace details is returned")    
    args=parser.parse_args()

class _Deployment:
    def __init__(self, namespace, logger):
        self.namespace = namespace
        if not self.namespace: self.namespace = 'all'
        self.k8s_object_list = K8sDeploy.get_deployments(self.namespace)
        self.k8s_object = 'deployments'
        self.logger = logger

    def check_deployment_security(self, v, l):
        headers = ['NAMESPACE', 'DEPLOYMENT', 'CONTAINER_NAME', 'PRIVILEGED_ESC', \
        'PRIVILEGED', 'READ_ONLY_FS', 'RUN_AS_NON_ROOT', 'RUNA_AS_USER']        
        data = k8s.Check.security_context(self.k8s_object, self.k8s_object_list, headers, \
        v, self.namespace, l, self.logger)
        if l: self.logger.info(data)

    def check_deployment_health_probes(self, v, l):
        headers = ['NAMESPACE', 'DEPLOYMENT', 'CONTAINER_NAME', \
        'READINESS_PROPBE', 'LIVENESS_PROBE']        
        data = k8s.Check.health_probes(self.k8s_object, self.k8s_object_list, headers, \
        v, self.namespace, l, self.logger)  
        if l: self.logger.info(data)

    def check_deployment_resources(self, v, l): 
        headers = ['NAMESPACE', 'DEPLOYMENT', 'CONTAINER_NAME', 'LIMITS', \
        'REQUESTS']       
        data = k8s.Check.resources(self.k8s_object, self.k8s_object_list, \
        headers, v, self.namespace, l, self.logger)
        if l: self.logger.info(data)

    def check_deployment_strategy(self, v, l): 
        headers = ['DEPLOYMENT', 'STRATEGY_TYPE']
        data = k8s.Check.strategy(self.k8s_object, self.k8s_object_list, headers, \
        v, self.namespace, l, self.logger)
        if l: self.logger.info(data)

    def check_replica(self, v, l): 
        headers = ['NAMESPACE', 'DEPLOYMENT', 'REPLICA_COUNT']
        data = k8s.Check.replica(self.k8s_object, self.k8s_object_list, headers,\
        v, self.namespace, l, self.logger)         
        if l: self.logger.info(data)

    def check_deployment_tolerations_affinity_node_selector_priority(self, v, l): 
        headers = ['NAMESPACE', 'DEPLOYMENT', 'NODE_SELECTOR', 'TOLERATIONS', \
        'AFFINITY', 'PRIORITY_CLASS']     
        data = k8s.Check.tolerations_affinity_node_selector_priority(self.k8s_object, \
        self.k8s_object_list, headers, v, self.namespace, l, self.logger)  
        if l: self.logger.info(data)     

def call_all(v, ns, l, logger):
    call = _Deployment(ns, logger)
    call.check_deployment_security(v, l)
    call.check_deployment_health_probes(v, l)
    call.check_deployment_resources(v, l)
    call.check_deployment_strategy(v, l)
    call.check_replica(v, l)
    call.check_deployment_tolerations_affinity_node_selector_priority(v, l)

def main():
    options = GetOpts.get_opts()
    logger = Logger.get_logger(options[4], '')
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