import sys, time, os, getopt
start_time = time.time()
from modules.main import ArgParse
from modules.logging import Logger
from modules.get_ds import K8sDaemonSet
from modules import process as k8s

class _Daemonset:
    def __init__(self, namespace, logger):
        self.namespace = namespace
        self.logger = logger
        if not self.namespace:
            self.namespace = 'all'
        self.k8s_object_list = K8sDaemonSet.get_damemonsets(self.namespace, self.logger)
        self.k8s_object = 'daemonset' 

    def check_damemonset_security(self, v, l):
        headers = ['NAMESPACE', 'DAEMONSET', 'CONTAINER_NAME', 'PRIVILEGED_ESC', \
        'PRIVILEGED', 'READ_ONLY_FS', 'RUN_AS_NON_ROOT', 'RUNA_AS_USER']        
        data = k8s.Check.security_context(self.k8s_object, self.k8s_object_list, \
        headers, v, self.namespace, l, self.logger)
        if l: self.logger.info(data)

    def check_damemonset_health_probes(self, v, l):
        headers = ['NAMESPACE', 'DAEMONSET', 'CONTAINER_NAME', \
        'READINESS_PROPBE', 'LIVENESS_PROBE']        
        data = k8s.Check.health_probes(self.k8s_object, self.k8s_object_list, \
        headers, v, self.namespace, l, self.logger)
        if l: self.logger.info(data)

    def check_damemonset_resources(self, v, l):
        headers = ['NAMESPACE', 'DAEMONSET', 'CONTAINER_NAME', \
        'LIMITS', 'REQUESTS']
        data = k8s.Check.resources(self.k8s_object, self.k8s_object_list, \
        headers, v, self.namespace, l, self.logger)
        if l: self.logger.info(data)

    def check_damemonset_tolerations_affinity_node_selector_priority(self, v, l):  
        headers = ['NAMESPACE', 'DAEMONSET', 'NODE_SELECTOR', \
        'TOLERATIONS', 'AFFINITY', 'PRIORITY_CLASS']
        data = k8s.Check.tolerations_affinity_node_selector_priority(\
        self.k8s_object, self.k8s_object_list, headers, v, self.namespace, l,  self.logger)
        if l: self.logger.info(data)

def call_all(v, namespace, l, logger):
    call = _Daemonset(namespace, logger)
    call.check_damemonset_security(v, l)
    call.check_damemonset_health_probes(v, l)
    call.check_damemonset_resources(v, l)
    call.check_damemonset_tolerations_affinity_node_selector_priority(v, l)

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