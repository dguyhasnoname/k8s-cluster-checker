from kubernetes import client, config
from kubernetes.client.rest import ApiException
import time, os, re
start_time = time.time()
from modules.main import GetOpts
from modules import logging as logger
from modules import process as k8s
from modules.load_kube_config import kubeConfig

kubeConfig.load_kube_config()
core = client.CoreV1Api()

class CtrlPlane:  
    global k8s_object, k8s_object_list, namespace, _logger
    _logger = logger.get_logger('CtrlPlane')
    namespace = 'kube-system'
    def check_ctrl_plane_pods():
        try:
            print ("\n[INFO] Fetching control plane workload data...")
            ctrl_plane_pods = core.list_namespaced_pod(namespace, \
            label_selector='tier=control-plane', timeout_seconds=10)
            if not ctrl_plane_pods.items:
                print (k8s.Output.RED + "[ERROR] " + k8s.Output.RESET \
                + "No control plane pods found with label 'tier=control-plane'")
                return
            return ctrl_plane_pods
        except ApiException as e:
            print("Exception when calling CoreV1Api->list_namespaced_pod: %s\n" % e)
    
    k8s_object_list = check_ctrl_plane_pods()
    k8s_object = 'pods'  

    def get_ctrl_plane_pods(l):
        if not k8s_object_list: return
        data = []
        headers = ['NAMESPACE', 'PODS', 'NODE_NAME', 'QoS']
        for item in k8s_object_list.items:
            data.append([item.metadata.namespace, item.metadata.name, \
            item.spec.node_name])
        data = k8s.Output.append_hyphen(data, '------------')
        data.append(["Total pods: ", len(data) - 1, ''])
        k8s.Output.print_table(data, headers, True, l)

    def check_ctrl_plane_security(v, l):
        headers = ['NAMESPACE', 'POD', 'CONTAINER_NAME', 'PRIVILEGED_ESC', \
        'PRIVILEGED', 'READ_ONLY_FS', 'RUN_AS_NON_ROOT', 'RUNA_AS_USER']        
        k8s.Check.security_context(k8s_object, k8s_object_list, headers, \
        v, namespace, l)

    def check_ctrl_plane_pods_health_probes(v, l):
        headers = ['NAMESPACE', 'PODS', 'CONTAINER_NAME', 'READINESS_PROPBE', \
        'LIVENESS_PROBE']        
        k8s.Check.health_probes(k8s_object, k8s_object_list, headers, \
        v, namespace, l)

    def check_ctrl_plane_pods_resources(v, l):
        headers = ['NAMESPACE', 'PODS', 'CONTAINER_NAME', 'LIMITS', 'REQUESTS']       
        k8s.Check.resources(k8s_object, k8s_object_list, headers, v, namespace, l)

    # gets file name from check_ctrl_plane_pods_properties function
    def check_ctrl_plane_pods_properties_operation(item, filename, headers, v, l):
        commands = item.spec.containers[0].command
        data = k8s.CtrlProp.compare_properties(filename, commands)
        k8s.Output.print_table(data, headers, v, l)

    def check_ctrl_plane_pods_qos(v, l):
        headers = ['NAMESPACE', 'POD', 'QoS']
        k8s.Check.qos(k8s_object, k8s_object_list, headers, v, namespace, l)

    def check_ctrl_plane_pods_properties(v, l):
        if not k8s_object_list: return
        container_name_check = ""
        headers = ['CTRL_PLANE_COMPONENT/ARGS', '']
        for item in k8s_object_list.items:
            if item.spec.containers[0].name in "kube-controller-manager" \
            and item.spec.containers[0].name not in container_name_check:
                CtrlPlane.check_ctrl_plane_pods_properties_operation(item,\
                './conf/kube-controller-manager', headers, v, l)

            elif item.spec.containers[0].name in "kube-apiserver" \
            and item.spec.containers[0].name not in container_name_check:
                CtrlPlane.check_ctrl_plane_pods_properties_operation(item,\
                './conf/kube-apiserver', headers, v, l)                
                json_data = k8s.CtrlProp.check_admission_controllers(\
                item.spec.containers[0].command, v, namespace, l)

                if l: _logger.info(json_data)

            elif item.spec.containers[0].name in "kube-scheduler" \
            and item.spec.containers[0].name not in container_name_check:
                CtrlPlane.check_ctrl_plane_pods_properties_operation(item,\
                './conf/kube-scheduler', headers, v, l)  
                k8s.CtrlProp.secure_scheduler_check(\
                item.spec.containers[0].command)
            container_name_check = item.spec.containers[0].name

def call_all(v, ns, l):
    CtrlPlane.get_ctrl_plane_pods(l)
    CtrlPlane.check_ctrl_plane_security(v, l)
    CtrlPlane.check_ctrl_plane_pods_health_probes(v, l)
    CtrlPlane.check_ctrl_plane_pods_resources(v, l)
    CtrlPlane.check_ctrl_plane_pods_qos(v, l)
    CtrlPlane.check_ctrl_plane_pods_properties(v, l)

def main():
    options = GetOpts.get_opts()
    if options[0]:
        usage()
    if options:
        call_all(options[1], options[2], options[3])
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