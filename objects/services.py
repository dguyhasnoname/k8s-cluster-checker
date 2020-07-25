from kubernetes import client, config
import sys, time, os, getopt
import objects as k8s
from modules.get_svc import K8sService

start_time = time.time()
config.load_kube_config()
core = client.CoreV1Api()

class _Service:
    global k8s_object, k8s_object_list, namespace
    k8s_object_list = K8sService.get_svc('all',core)
    k8s_object = 'services'

    def list_service(v):
        data = []
        headers = ['NAMESPACE', 'SERVICE', 'CLUSTER_IP', 'SELECTOR']
        for item in k8s_object_list.items:
            if item.spec.selector:
                for i in item.spec.selector:
                    app_label = i
                    break
                data.append([item.metadata.namespace, item.metadata.name, \
                item.spec.cluster_ip, app_label + ": " + item.spec.selector[app_label]])
            else:
                data.append([item.metadata.namespace, item.metadata.name, \
                item.spec.cluster_ip, "None"])
        data.append(['----------', '---', '---', '---'])
        data.append(["Total: " , len(data) - 1 , '-', '-'])
        k8s.Output.print_table(data,headers,True)

    def analyse_service(v):
        data, cluster_ip_svc, lb_svc, others_svc = [], [], [], []
        if v:
            for item in k8s_object_list.items:
                if 'ClusterIP' in item.spec.type:
                    cluster_ip_svc.append([item.metadata.namespace, item.metadata.name])
                elif 'LoadBalancer' in item.spec.type:
                    lb_svc.append([item.metadata.namespace, item.metadata.name])
                else:
                    others_svc.append([item.metadata.namespace, item.metadata.name])
            k8s.Output.bar(cluster_ip_svc, k8s_object_list.items, 'out of ' + \
            str(len(k8s_object_list.items)) + ' services are of type', k8s_object, 'ClusterIP')
            k8s.Output.bar(lb_svc, k8s_object_list.items, 'out of ' + \
            str(len(k8s_object_list.items)) + ' services are of type', k8s_object, 'LoadBalancer')
            k8s.Output.bar(others_svc, k8s_object_list.items, 'out of ' + \
            str(len(k8s_object_list.items)) + ' services are of type', k8s_object, 'others')

def call_all(v):
    _Service.list_service(v)
    _Service.analyse_service(v)

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

    print(k8s.Output.GREEN + "\nTotal time taken: " + k8s.Output.RESET + \
    "{}s".format(round((time.time() - start_time), 2)))     

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(k8s.Output.RED + "[ERROR] " + k8s.Output.RESET + 'Interrupted from keyboard!')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)    