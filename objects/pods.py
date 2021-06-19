import time, os, argparse, sys
start_time = time.time()
from modules.main import ArgParse
from modules.logging import Logger
from modules import process as k8s
from modules.get_pods import K8sPods

class _Pods:
    def __init__(self, namespace, logger):
        self.logger = logger
        if not namespace:
            self.namespace = 'all'  
        else:
            self.namespace = namespace
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
    args = ArgParse.arg_parse()
    # args is [u, verbose, ns, l, format, silent]
    logger = Logger.get_logger(args.format, args.silent)
    if args:
        call_all(args.verbose, args.namespace, args.logging, logger)
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