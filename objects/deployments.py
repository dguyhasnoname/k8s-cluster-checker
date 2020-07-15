from kubernetes import client, config
from kubernetes.client.rest import ApiException
import sys, time, os 
import datetime
import objects as k8s

start_time = time.time()
config.load_kube_config()
apps = client.AppsV1Api()

class Deployment:
    global k8s_object, k8s_object_list, namespace
    def get_deployments():
        try:
            namespace = 'kube-system'
            deployments = apps.list_namespaced_deployment(namespace, timeout_seconds=10)
            return deployments
        except ApiException as e:
            print("Exception when calling AppsV1Api->read_namespaced_deployment: %s\n" % e)

    k8s_object_list = get_deployments()
    k8s_object = 'deployment'

    def check_deployment_security():
        headers = ['DEPLOYMENT', 'CONTAINER_NAME', 'PRIVILEGED_ESC', \
        'PRIVILEGED', 'READ_ONLY_FS', 'RUN_AS_NON_ROOT', 'RUNA_AS_USER']        
        data = k8s.Check.security_context(k8s_object,k8s_object_list)
        k8s.Output.print_table(data,headers)

    def check_deployment_health_probes():
        headers = ['DEPLOYMENT', 'CONTAINER_NAME', 'READINESS_PROPBE', 'LIVENESS_PROBE']        
        data = k8s.Check.health_probes(k8s_object,k8s_object_list)
        k8s.Output.print_table(data,headers)  

    def check_deployment_resources(): 
        headers = ['DEPLOYMENT', 'CONTAINER_NAME', 'LIMITS', 'REQUESTS']       
        data = k8s.Check.resources(k8s_object,k8s_object_list)
        k8s.Output.print_table(data,headers) 

    def check_deployment_strategy(): 
        headers = ['DEPLOYMENT', 'CONTAINER_NAME', 'STRATEGY_TYPE']
        data = k8s.Check.strategy(k8s_object,k8s_object_list)
        k8s.Output.print_table(data,headers)  

    def check_deployment_tolerations_affinity_node_selector_priority(): 
        headers = ['DEPLOYMENT', 'NODE_SELECTOR', 'TOLERATIONS', 'AFFINITY', 'PRIORITY_CLASS']     
        data = k8s.Check.tolerations_affinity_node_selector_priority(k8s_object,k8s_object_list)
        k8s.Output.print_table(data,headers)       

def main():
    Deployment.check_deployment_security()
    Deployment.check_deployment_health_probes()
    Deployment.check_deployment_resources()
    Deployment.check_deployment_strategy()
    Deployment.check_deployment_tolerations_affinity_node_selector_priority()
    print(k8s.Output.GREEN + "Total time taken: " + k8s.Output.RESET + "{}s".format(round((time.time() - start_time), 2)))

if __name__ == "__main__":
    main()