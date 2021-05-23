import sys, time, os, getopt, argparse, re
start_time = time.time()
from modules.main import GetOpts
from modules.logging import Logger
from modules import process as k8s
from modules.get_nodes import K8sNodes

class _Nodes:
    def __init__(self, logger):
        self.logger = logger

    global k8s_object, k8s_object_list, k8s_node
    # k8s_object = 'nodes'
    # logger = Logger.get_logger('', '')

    def get_nodes_details(self, v, l):
        data = []
        logger = self.logger
        k8s_object_list = K8sNodes.get_nodes(logger)
        headers = ['NODE_NAME', 'K8S_VERSION', 'ROLE', 'NODE_CPU', 'NODE_MEM_GB', \
        'VOLUMES_USED/ATTACHED', 'POD_CIDR', 'OS_NAME', 'DOCKER_VERSION', 'INSTANCE_TYPE', 'REGION']
        for item in k8s_object_list.items:
            node_memory_gb = round((int(re.sub('\D', '', item.status.capacity['memory'])) / 1000000), 1)
            docker_version = item.status.node_info.container_runtime_version.rsplit('//', 1)[1]
            role_tag = ['kubernetes.io/role', 'node.kubernetes.io/role']          
            if 'kubernetes.io/role' in item.metadata.labels:
                tag = item.metadata.labels['kubernetes.io/role']
            elif 'node.kubernetes.io/role' in item.metadata.labels:
                tag = item.metadata.labels['node.kubernetes.io/role']
            elif 'node-role.kubernetes.io/master' in item.metadata.labels:
                tag = 'master'
            elif 'node-role.kubernetes.io/node' in item.metadata.labels:
                tag = 'node'
            elif 'node-role.kubernetes.io/etcd' in item.metadata.labels:
                tag = 'etcd'
            else:
                tag = 'others'
            if 'node.kubernetes.io/instance-type' in item.metadata.labels:
                instance_type = item.metadata.labels['node.kubernetes.io/instance-type']
            else:
                instance_type = u'\u2717'
            if 'topology.kubernetes.io/region' in item.metadata.labels:
                region = item.metadata.labels['topology.kubernetes.io/region']
            else:
                region = u'\u2717'
            if item.status.volumes_in_use:
                volumes_used = len(item.status.volumes_in_use)
            else:
                volumes_used = u'\u2717'
            volumes = ""
            if item.status.volumes_attached:
                volumes_attached = len(item.status.volumes_attached)
                volumes = str(volumes_used) + '/' + str(volumes_attached)
            else:
                volumes_attached = u'\u2717'
                volumes = u'\u2717'

            data.append([item.metadata.name, item.status.node_info.kubelet_version, \
            tag, item.status.capacity['cpu'], \
            node_memory_gb, volumes, item.spec.pod_cidr, item.status.node_info.os_image, \
            docker_version, instance_type, region, volumes_used, volumes_attached])
            
        k8s.Output.csv_out(data, headers, 'nodes', 'detail', '')
        json_out = k8s.Output.json_out(data, '', headers, 'nodes', 'detail', '')

        if l: logger.info(json_out)
        
        total_cpu, total_mem, masters, nodes, etcd, others, \
        total_vol = 0, 0, 0, 0, 0, 0, 0
        for i in data:
            total_cpu += int(i[3])
            total_mem += i[4]
            if i[2] == 'master': masters += 1
            if i[2] == 'node': nodes += 1
            if i[2] == 'etcd': etcd += 1
            if i[2] == 'others': others += 1
            if i[11] != u'\u2717': total_vol += i[11]

        total_nodes = 'total:  ' + str(masters+nodes+etcd+others)
        node_types = 'masters: ' + str(masters) + "\n" + 'worker:  ' \
        + str(nodes) + "\n" + 'etcd:    ' + str(etcd) + "\n" + \
        "others:  " + str(others)
        data = k8s.Output.append_hyphen(data, '----------')

        data.append([total_nodes, item.status.node_info.kubelet_version, \
        node_types, total_cpu, f'{round(total_mem, 2)}GB', total_vol, u'\u2717', \
        item.status.node_info.os_image, docker_version, u'\u2717', \
        u'\u2717', '', ''])
        if v:
            k8s.Output.print_table(data, headers, v, l)
        else:
            # print summary of nodes from last line of data list
            for i in data[-1:]:
                short_data = [[i[2], i[1], i[3], i[4], i[7], i[8], i[5]]]
                short_data.append(['----------', '', '', '', '', '', ''])
                short_data.append(['total:   ' \
                + str(masters+nodes+etcd+others), '', '', '', '', '', ''])
            headers = ['TOTAL_NODES', 'K8S_VERSION', 'TOTAL_CPU', \
            'TOTAL_MEM_GB', 'OS_NAME', 'DOCKER_VERSION', 'VOLUMES_IN_USE']
            k8s.Output.print_table(short_data, headers, True, l)

        logger.info ("Checking for latest and installed versions.")
        data_version_check = k8s.Nodes.node_version_check(item.status.node_info.os_image, \
        docker_version, item.status.node_info.kubelet_version, l, logger)
        
        if l: logger.info(data_version_check)

def call_all(v, l):
    _Nodes.get_nodes_details(v, l)

def main():
    options = GetOpts.get_opts()
    if options[0]:
        usage()
    if options:
        call_all(options[1], options[3])
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