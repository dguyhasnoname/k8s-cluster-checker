from kubernetes import client, config
from kubernetes.client.rest import ApiException
import sys, time, os, getopt, argparse, re
start_time = time.time()
import objects as k8s
from modules.get_nodes import K8sNodes

config.load_kube_config()
core = client.CoreV1Api()
apps = client.AppsV1Api()

class _Nodes:
    global k8s_object, k8s_object_list
    k8s_object_list = K8sNodes.get_nodes(core)
    k8s_object = 'nodes'

    def get_nodes_details(v):
        data = []
        headers = ['NODE_NAME', 'K8S_VERSION', 'ROLE', 'NODE_CPU', 'NODE_MEM_GB', 'POD_CIDR', 'OS_NAME', 'DOCKER_VERSION']
        for item in k8s_object_list.items:
            for i in item.metadata.labels:
                node_memory_gb = round((int(re.sub('\D', '', item.status.capacity['memory'])) / 1000000), 1)
                docker_version = item.status.node_info.container_runtime_version.rsplit('//', 1)[1]
                #instance_type = item.metadata.labels['beta.kubernetes.io/instance-type']

            data.append([item.metadata.name, item.status.node_info.kubelet_version, \
            item.metadata.labels['kubernetes.io/role'], item.status.capacity['cpu'], \
            node_memory_gb, item.spec.pod_cidr, item.status.node_info.os_image, \
            docker_version])   
            
        total_cpu, total_mem, masters, nodes, etcd = 0, 0, 0, 0, 0
        for i in data:
            total_cpu = total_cpu + int(i[3])
            total_mem = total_mem + i[4]
            if i[2] == 'master': masters += 1
            if i[2] == 'node': nodes += 1
            if i[2] == 'etcd' : etcd += 1
        total_nodes = f'masters: {masters} etcd: {etcd} worker: {nodes}'
        data.append(['----------', '-----', '-----', '-----', '-----', '-----', '-----', '-----'])
        data.append([total_nodes, item.status.node_info.kubelet_version, \
        "-", total_cpu, f'{round(total_mem, 2)}GB', "-", item.status.node_info.os_image, docker_version])          
        if v:
            k8s.Output.print_table(data,headers,v)
        else:
            for i in data[-1:]:
                short_data = [[i[0], i[1], i[3], i[4], i[6], i[7]]]
            headers = ['TOTAL_NODES', 'K8S_VERSION', 'TOTAL_CPU', 'TOTAL_MEM_GB', 'OS_NAME', 'DOCKER_VERSION']
            k8s.Output.print_table(short_data,headers,True)

def call_all(v):
    _Nodes.get_nodes_details(v)

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hv", ["help", "verbose"])
        if not opts:        
            call_all("")
            
    except getopt.GetoptError as err:
        # print help information and exit:
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

    print(k8s.Output.GREEN + "Total time taken: " + k8s.Output.RESET + \
    "{}s".format(round((time.time() - start_time), 2)))

if __name__ == "__main__":
    main()