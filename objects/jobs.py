import sys, time, os, getopt
import objects as k8s
start_time = time.time()
from modules.get_jobs import K8sJobs

class Jobs:
    global k8s_object, k8s_object_list, namespace
    k8s_object_list = K8sJobs.get_jobs('all')
    k8s_object = 'jobs'

    def list_jobs(v):
        data = []
        headers = ['NAMESPACE', 'JOBS']
        for item in k8s_object_list.items:
            data.append([item.metadata.namespace, item.metadata.name])
        data.append(['----------', '---'])
        data.append(["Total: " , len(data) - 1])
        k8s.Output.print_table(data,headers,True)

    def check_jobs_pod_security(v):
        headers = ['NAMESPACE', 'JOBS', 'CONTAINER_NAME', 'PRIVILEGED_ESC', \
        'PRIVILEGED', 'READ_ONLY_FS', 'RUN_AS_NON_ROOT', 'RUNA_AS_USER']        
        data = k8s.Check.security_context(k8s_object,k8s_object_list)
        k8s.Output.print_table(data,headers,v)

    def check_jobs_pod_health_probes(v):
        headers = ['NAMESPACE', 'JOBS', 'CONTAINER_NAME', 'READINESS_PROPBE', 'LIVENESS_PROBE']        
        data = k8s.Check.health_probes(k8s_object,k8s_object_list)
        k8s.Output.print_table(data,headers,v)  

    def check_jobs_pod_resources(v): 
        headers = ['NAMESPACE', 'JOBS', 'CONTAINER_NAME', 'LIMITS', 'REQUESTS']       
        data = k8s.Check.resources(k8s_object,k8s_object_list)
        k8s.Output.print_table(data,headers,v)         

    def check_jobs_pod_tolerations_affinity_node_selector_priority(v): 
        headers = ['NAMESPACE', 'JOBS', 'NODE_SELECTOR', 'TOLERATIONS', 'AFFINITY', 'PRIORITY_CLASS']     
        data = k8s.Check.tolerations_affinity_node_selector_priority(k8s_object,k8s_object_list)
        k8s.Output.print_table(data,headers,v)

def call_all(v):
    Jobs.list_jobs(v)
    Jobs.check_jobs_pod_security(v)
    Jobs.check_jobs_pod_health_probes(v)
    Jobs.check_jobs_pod_resources(v)
    Jobs.check_jobs_pod_tolerations_affinity_node_selector_priority(v)

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
            verbose = True
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