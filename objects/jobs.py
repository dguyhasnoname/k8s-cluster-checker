import time, os, sys
start_time = time.time()
from modules.main import ArgParse
from modules.logging import Logger
from modules import process as k8s
from modules.get_jobs import K8sJobs

class Jobs:
    def __init__(self, namespace, logger):
        self.namespace = namespace
        self.logger = logger
        if not self.namespace:
            self.namespace = 'all'
        self.k8s_object_list = K8sJobs.get_jobs(self.namespace, self.logger)
        try:
            len(self.k8s_object_list.items)
        except:
            logger.warning("No jobs found!")
            sys.exit()
        self.k8s_object = 'jobs'

    def list_jobs(self, v, l):
        data = []
        headers = ['NAMESPACE', 'JOBS']
        for item in self.k8s_object_list.items:
            data.append([item.metadata.namespace, item.metadata.name])
        data = k8s.Output.append_hyphen(data, '---------')
        data.append(["Total: " , len(data) - 1])
        k8s.Output.print_table(data, headers, True, l)

    def check_jobs_pod_security(self, v, l):
        headers = ['NAMESPACE', 'JOBS', 'CONTAINER_NAME', 'PRIVILEGED_ESC', \
        'PRIVILEGED', 'READ_ONLY_FS', 'RUN_AS_NON_ROOT', 'RUNA_AS_USER']        
        data = k8s.Check.security_context(self.k8s_object, self.k8s_object_list, headers, \
        v, self.namespace, l, self.logger)
        if l: self.logger.info(data)

    def check_jobs_pod_health_probes(self, v, l):
        headers = ['NAMESPACE', 'JOBS', 'CONTAINER_NAME', 'READINESS_PROPBE', \
        'LIVENESS_PROBE']        
        data = k8s.Check.health_probes(self.k8s_object, self.k8s_object_list, headers, \
        v, self.namespace, l, self.logger)
        if l: self.logger.info(data) 

    def check_jobs_pod_resources(self, v, l): 
        headers = ['NAMESPACE', 'JOBS', 'CONTAINER_NAME', 'LIMITS', 'REQUESTS']       
        data = k8s.Check.resources(self.k8s_object, self.k8s_object_list, headers, \
        v, self.namespace, l, self.logger)
        if l: self.logger.info(data)         

    def check_jobs_pod_tolerations_affinity_node_selector_priority(self, v, l): 
        headers = ['NAMESPACE', 'JOBS', 'NODE_SELECTOR', 'TOLERATIONS', \
        'AFFINITY', 'PRIORITY_CLASS']     
        data = k8s.Check.tolerations_affinity_node_selector_priority(self.k8s_object, \
        self.k8s_object_list, headers, v, self.namespace, l, self.logger)
        if l: self.logger.info(data)

def call_all(v, namespace, l, logger):
    call = Jobs(namespace, logger)
    call.list_jobs(v, l)
    call.check_jobs_pod_security(v, l)
    call.check_jobs_pod_health_probes(v, l)
    call.check_jobs_pod_resources(v, l)
    call.check_jobs_pod_tolerations_affinity_node_selector_priority(v, l)

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