from kubernetes import client, config
from kubernetes.client.rest import ApiException
import sys, time, os, re, getopt
from modules import process as k8s

start_time = time.time()
config.load_kube_config()
core = client.CoreV1Api()

class CtrlPlane:
    global k8s_object, k8s_object_list, namespace
    def check_ctrl_plane_pods():
        namespace = 'kube-system'
        try:
            ctrl_plane_pods = core.list_namespaced_pod(namespace, \
            label_selector='tier=control-plane', timeout_seconds=10)
            return ctrl_plane_pods
        except ApiException as e:
            print("Exception when calling CoreV1Api->list_namespaced_pod: %s\n" % e)
    
    k8s_object_list = check_ctrl_plane_pods()
    k8s_object = 'pods'

    def get_ctrl_plane_pods():
        data = []
        headers = ['NAMESPACE', 'PODS', 'CONTAINER_NAME']
        for item in k8s_object_list.items:
            data.append([item.metadata.namespace, item.metadata.name])
        data.append(['----------', '---'])
        data.append(["Total pods: ", len(data) - 1])
        k8s.Output.print_table(data,headers,True)

    def check_ctrl_plane_pods_health_probes(v):
        headers = ['NAMESPACE', 'PODS', 'CONTAINER_NAME', 'READINESS_PROPBE', 'LIVENESS_PROBE']        
        data = k8s.Check.health_probes(k8s_object,k8s_object_list)
        k8s.Output.print_table(data,headers,v)   

    def check_ctrl_plane_pods_resources(v):
        headers = ['NAMESPACE', 'PODS', 'CONTAINER_NAME', 'LIMITS', 'REQUESTS']       
        data = k8s.Check.resources(k8s_object,k8s_object_list)
        k8s.Output.print_table(data,headers,v)

    def check_ctrl_plane_pods_properties_operation(item,filename,headers,v):
        commands = item.spec.containers[0].command
        data = k8s.CtrlProp.compare_properties(filename, commands)
        k8s.Output.print_table(data,headers,v)

    def check_ctrl_plane_pods_properties(v):
        container_name_check = ""
        headers = ['CTRL_PLANE_COMPONENT/ARGS', '']
        for item in k8s_object_list.items:
            if item.spec.containers[0].name in "kube-controller-manager" \
            and item.spec.containers[0].name not in container_name_check:
                CtrlPlane.check_ctrl_plane_pods_properties_operation(item,\
                './conf/kube-controller-manager',headers,v)

            elif item.spec.containers[0].name in "kube-apiserver" \
            and item.spec.containers[0].name not in container_name_check:
                CtrlPlane.check_ctrl_plane_pods_properties_operation(item,\
                './conf/kube-apiserver',headers,v)                
                k8s.CtrlProp.check_admission_controllers(item.spec.containers[0].command,v)

            elif item.spec.containers[0].name in "kube-scheduler" \
            and item.spec.containers[0].name not in container_name_check:
                CtrlPlane.check_ctrl_plane_pods_properties_operation(item,\
                './conf/kube-scheduler',headers,v)  
                k8s.CtrlProp.secure_scheduler_check(item.spec.containers[0].command)
            container_name_check = item.spec.containers[0].name

def call_all(v):
    CtrlPlane.get_ctrl_plane_pods()
    CtrlPlane.check_ctrl_plane_pods_health_probes(v)
    CtrlPlane.check_ctrl_plane_pods_resources(v)
    CtrlPlane.check_ctrl_plane_pods_properties(v)

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hv", ["help", "verbose"])
        if not opts:        
            call_all(False)
            
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