from kubernetes import client, config
from kubernetes.client.rest import ApiException
import sys, time, os 
import datetime
import objects as k8s

start_time = time.time()
config.load_kube_config()
core = client.CoreV1Api()

class CtrlPlane:
    global k8s_object, k8s_object_list, namespace
    def check_ctrl_plane_pods():
        namespace = 'kube-system'
        try:
            ctrl_plane_pods = core.list_namespaced_pod(namespace, label_selector='tier=control-plane', timeout_seconds=10)
            return ctrl_plane_pods
        except ApiException as e:
            print("Exception when calling CoreV1Api->list_namespaced_pod: %s\n" % e)
    
    k8s_object_list = check_ctrl_plane_pods()
    k8s_object = 'pod'

    def check_ctrl_plane_pods_health_probes():
        headers = ['PODS', 'CONTAINER_NAME', 'READINESS_PROPBE', 'LIVENESS_PROBE']        
        data = k8s.Check.health_probes(k8s_object,k8s_object_list)
        k8s.Output.print_table(data,headers)   

    def check_ctrl_plane_pods_resources():
        headers = ['PODS', 'CONTAINER_NAME', 'LIMITS', 'REQUESTS']       
        data = k8s.Check.resources(k8s_object,k8s_object_list)
        k8s.Output.print_table(data,headers)

    def check_ctrl_plane_pods_properties():
        data = []
        headers = ['PODS', 'CONTAINER_NAME', 'READINESS_PROPBE', 'LIVENESS_PROBE'] 
        # no loop for container as in 'V1PodSpec' object is not iterable
        for item in k8s_object_list.items:
            for c in item.spec.containers[0].command:
                data.append([item.metadata.name, item.spec.containers[0].command])
        k8s.Output.print_table(data,headers)

def main():
    CtrlPlane.check_ctrl_plane_pods_health_probes()
    CtrlPlane.check_ctrl_plane_pods_resources()
    CtrlPlane.check_ctrl_plane_pods_properties()
    print(k8s.Output.GREEN + "Total time taken: " + k8s.Output.RESET + "{}s".format(round((time.time() - start_time), 2)))

if __name__ == "__main__":
    main()    