from kubernetes import client, config
from kubernetes.client.rest import ApiException
import time, os, re, sys
start_time = time.time()
from modules.main import ArgParse
from modules.logging import Logger
from modules import process as k8s
from modules.load_kube_config import kubeConfig

kubeConfig.load_kube_config()
core = client.CoreV1Api()

class CtrlPlane:
    def __init__(self, logger):
        self.logger = logger
        self.k8s_object_list = ''
        self.namespace = 'kube-system'
        self.k8s_object = 'pods'
    
    global k8s_object, k8s_object_list, namespace
    def check_ctrl_plane_pods(self):
        try:
            print ("\n[INFO] Fetching control plane workload data...")
            ctrl_plane_pods = core.list_namespaced_pod(self.namespace, \
            label_selector='tier=control-plane', timeout_seconds=10)
            if not ctrl_plane_pods.items:
                print (k8s.Output.RED + "[ERROR] " + k8s.Output.RESET \
                + "No control plane pods found with label 'tier=control-plane'")
                return
            return ctrl_plane_pods
        except ApiException as e:
            print("Exception when calling CoreV1Api->list_namespaced_pod: %s\n" % e) 

    def get_ctrl_plane_pods(self, l):
        self.k8s_object_list = CtrlPlane.check_ctrl_plane_pods(self)
        if not self.k8s_object_list: return
        data = []
        headers = ['NAMESPACE', 'PODS', 'NODE_NAME', 'QoS']
        for item in self.k8s_object_list.items:
            data.append([item.metadata.namespace, item.metadata.name, \
            item.spec.node_name])
        data = k8s.Output.append_hyphen(data, '------------')
        data.append(["Total pods: ", len(data) - 1, ''])
        k8s.Output.print_table(data, headers, True, l)

    def check_ctrl_plane_security(self, v, l):
        headers = ['NAMESPACE', 'POD', 'CONTAINER_NAME', 'PRIVILEGED_ESC', \
        'PRIVILEGED', 'READ_ONLY_FS', 'RUN_AS_NON_ROOT', 'RUNA_AS_USER']        
        k8s.Check.security_context(self.k8s_object, self.k8s_object_list, headers, \
        v, self.namespace, l, self.logger)

    def check_ctrl_plane_pods_health_probes(self, v, l):
        headers = ['NAMESPACE', 'PODS', 'CONTAINER_NAME', 'READINESS_PROPBE', \
        'LIVENESS_PROBE']        
        k8s.Check.health_probes(self.k8s_object, self.k8s_object_list, headers, \
        v, self.namespace, l, self.logger)

    def check_ctrl_plane_pods_resources(self, v, l):
        headers = ['NAMESPACE', 'PODS', 'CONTAINER_NAME', 'LIMITS', 'REQUESTS']       
        k8s.Check.resources(self.k8s_object, self.k8s_object_list, headers, v, \
        self.namespace, l, self.logger)

    # gets file name from check_ctrl_plane_pods_properties function
    def check_ctrl_plane_pods_properties_operation(item, filename, headers, v, l):
        commands = item.spec.containers[0].command
        data = k8s.CtrlProp.compare_properties(filename, commands)
        k8s.Output.print_table(data, headers, v, l)

    def check_ctrl_plane_pods_qos(self, v, l):
        headers = ['NAMESPACE', 'POD', 'QoS']
        k8s.Check.qos(self.k8s_object, self.k8s_object_list, headers, v, \
        self.namespace, l, self.logger)

    def check_ctrl_plane_pods_properties(self, v, l):
        if not self.k8s_object_list: return
        container_name_check = ""
        headers = ['CTRL_PLANE_COMPONENT/ARGS', '']
        k8scc_dir = os.path.dirname(__file__)
        for item in self.k8s_object_list.items:
            if item.spec.containers[0].name in "kube-controller-manager" \
            and item.spec.containers[0].name not in container_name_check:
                CtrlPlane.check_ctrl_plane_pods_properties_operation(item,\
                os.path.join(k8scc_dir, 'conf/kube-controller-manager'), headers, v, l)

            elif item.spec.containers[0].name in "kube-apiserver" \
            and item.spec.containers[0].name not in container_name_check:
                CtrlPlane.check_ctrl_plane_pods_properties_operation(item,\
                os.path.join(k8scc_dir, 'conf/kube-apiserver'), headers, v, l)                
                json_data = k8s.CtrlProp.check_admission_controllers(\
                item.spec.containers[0].command, v, self.namespace, l, k8scc_dir)

                if l: self.logger.info(json_data)

            elif item.spec.containers[0].name in "kube-scheduler" \
            and item.spec.containers[0].name not in container_name_check:
                CtrlPlane.check_ctrl_plane_pods_properties_operation(item,\
                os.path.join(k8scc_dir, 'conf/kube-scheduler'), headers, v, l)  
                k8s.CtrlProp.secure_scheduler_check(\
                item.spec.containers[0].command)
            container_name_check = item.spec.containers[0].name

def call_all(v, ns, l, logger):
    call = CtrlPlane(logger)
    call.get_ctrl_plane_pods(l)
    call.check_ctrl_plane_security(v, l)
    call.check_ctrl_plane_pods_health_probes(v, l)
    call.check_ctrl_plane_pods_resources(v, l)
    call.check_ctrl_plane_pods_qos(v, l)
    call.check_ctrl_plane_pods_properties(v, l)

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