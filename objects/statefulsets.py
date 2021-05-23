import sys, time, os, getopt
start_time = time.time()
from modules.main import GetOpts
from modules.logging import Logger
from modules import process as k8s
from modules.get_sts import K8sStatefulSet

class _Sts:
    def __init__(self, namespace, logger):
        self.namespace = namespace
        self.logger = logger
        if not self.namespace:
            self.namespace = 'all'
        self.k8s_object_list = K8sStatefulSet.get_sts(self.namespace, self.logger)    
        self.k8s_object = 'statefulsets'

    def check_sts_security(self, v, l):
        headers = ['NAMESPACE', 'STATEFULSET', 'CONTAINER_NAME', 'PRIVILEGED_ESC', \
        'PRIVILEGED', 'READ_ONLY_FS', 'RUN_AS_NON_ROOT', 'RUNA_AS_USER']        
        data = k8s.Check.security_context(self.k8s_object, self.k8s_object_list, headers, \
        v, self.namespace, l, self.logger)
        if l: self.logger.info(data)

    def check_sts_health_probes(self, v, l):
        headers = ['NAMESPACE', 'STATEFULSET', 'CONTAINER_NAME', \
        'READINESS_PROPBE', 'LIVENESS_PROBE']        
        data = k8s.Check.health_probes(self.k8s_object, self.k8s_object_list, headers, \
        v, self.namespace, l, self.logger)
        if l: self.logger.info(data)

    def check_sts_resources(self, v, l):
        headers = ['NAMESPACE', 'STATEFULSET', 'CONTAINER_NAME', \
        'LIMITS', 'REQUESTS']
        data = k8s.Check.resources(self.k8s_object, self.k8s_object_list, headers, \
        v, self.namespace, l, self.logger)
        if l: self.logger.info(data)

    def check_sts_tolerations_affinity_node_selector_priority(self, v, l):  
        headers = ['NAMESPACE', 'STATEFULSET', 'NODE_SELECTOR', \
        'TOLERATIONS', 'AFFINITY', 'PRIORITY_CLASS']
        data = k8s.Check.tolerations_affinity_node_selector_priority(self.k8s_object, \
        self.k8s_object_list, headers, v, self.namespace, l, self.logger)
        if l: self.logger.info(data)

def call_all(v, ns, l, logger):
    call = _Sts(ns, logger)
    call.check_sts_security(v, l)
    call.check_sts_health_probes(v, l)
    call.check_sts_resources(v, l)
    call.check_sts_tolerations_affinity_node_selector_priority(v, l)

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