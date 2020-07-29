from columnar import columnar
from click import style
from packaging import version
import os, re, time, requests, json

class Output:
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    CYAN = '\033[36m'
    RESET = '\033[0m'  
    BOLD = '\033[1;30m'
    # u'\u2717' means values is None or not defined
    # u'\u2714' means value is defined
    
    global patterns
    patterns = [(u'\u2714', lambda text: style(text, fg='green')), \
                ('True', lambda text: style(text, fg='green')), \
                ('False', lambda text: style(text, fg='yellow'))]
    
    def time_taken(start_time):
        print(Output.GREEN + "\nTotal time taken: " + Output.RESET + \
        "{}s".format(round((time.time() - start_time), 2)))         

    def separator(color,char):
        columns, rows = os.get_terminal_size(0)
        for i in range(columns):
            print (color + char, end="" + Output.RESET )
        print ("\n")
   
    def print_table(data,headers,verbose):
        if verbose and len(data) != 0:
            table = columnar(data, headers, no_borders=True, patterns=patterns, row_sep='-')
            print (table)
        else:
            return

    def bar(not_defined,data,message,k8s_object,config,color):
        show_bar = []
        if len(not_defined) == 0:
            return
        percentage = round(((100.0 * len(not_defined) / len(data))), 2)

        for i in range(25):
            if int(i) < percentage / 4: 
                show_bar.append(u'\u2588')
            else:
                show_bar.append(u'\u2591')

        if percentage != 0:
            print (color + "{}".format("".join(show_bar)) + Output.RESET + " {}% | {} {} {} {}.".format(percentage, \
            len(not_defined), k8s_object, message, config))
        else:
            print (Output.GREEN + "All {} has {} defined.".format(k8s_object,config) + Output.RESET)       

class Check:
    def security_context(k8s_object,k8s_object_list):
        data, config_not_defined, privileged_containers, run_as_user, \
        allow_privilege_escalation, read_only_root_filesystem, \
        run_as_non_root = [], [], [], [], [], [], []
        config = 'security context'
        for item in k8s_object_list.items:
            k8s_object_name = item.metadata.name
            if 'pods' in k8s_object:
                containers = item.spec.containers
            else:
                containers = item.spec.template.spec.containers            
            for container in containers:
                if container.security_context is not None:
                    data.append([item.metadata.namespace, k8s_object_name, container.name, \
                    container.security_context.allow_privilege_escalation, \
                    container.security_context.privileged,  \
                    container.security_context.read_only_root_filesystem, \
                    container.security_context.run_as_non_root, \
                    container.security_context.run_as_user ])
                    if container.security_context.privileged: privileged_containers.append(True)
                    if container.security_context.run_as_user: run_as_user.append(True)
                    if container.security_context.allow_privilege_escalation: allow_privilege_escalation.append(True)
                    if container.security_context.read_only_root_filesystem: read_only_root_filesystem.append(True)
                    if container.security_context.run_as_non_root: run_as_non_root.append(True)
                else:
                    data.append([item.metadata.namespace, k8s_object_name, container.name, \
                    u'\u2717', u'\u2717', u'\u2717', u'\u2717', u'\u2717'])  
                    config_not_defined.append(True)

        print ("\n{}: {} {}".format(config, len(k8s_object_list.items), k8s_object))
        Output.bar(config_not_defined, data, "container's with no",k8s_object,config, Output.RED)
        Output.bar(privileged_containers, data,'have', k8s_object, \
        'privileged containers running', Output.RED)
        Output.bar(allow_privilege_escalation, data,'have containers running in', \
        k8s_object,'allow privilege escalation mode', Output.RED)
        Output.bar(run_as_user, data, "container's running have", k8s_object, 'user defined', Output.GREEN)
        Output.bar(run_as_non_root, data,"container's running with", k8s_object, 'non root user', Output.GREEN)
        Output.bar(read_only_root_filesystem, data, "container's running have", \
        k8s_object,'read-only root filesystem', Output.GREEN)

        return data

    def health_probes(k8s_object,k8s_object_list):
        data, config_not_defined, readiness_probe, liveness_probe, both = [], [], [], [], []
        config = 'health checks'
        for item in k8s_object_list.items:
            k8s_object_name = item.metadata.name
            if 'pods' in k8s_object:
                containers = item.spec.containers
            else:
                containers = item.spec.template.spec.containers
            for container in containers:
                if container.readiness_probe is not None and container.liveness_probe is not None:
                    data.append([item.metadata.namespace, k8s_object_name, container.name, u'\u2714', u'\u2714']) 
                    both.append(True)
                elif container.readiness_probe is None and container.liveness_probe is not None:
                    data.append([item.metadata.namespace, k8s_object_name, container.name, u'\u2717', u'\u2714'])
                    liveness_probe.append(True)                       
                elif container.readiness_probe is not None and container.liveness_probe is None:
                    data.append([item.metadata.namespace, k8s_object_name, container.name, u'\u2714', u'\u2717']) 
                    readiness_probe.append(True)
                else:
                    data.append([item.metadata.namespace, k8s_object_name, container.name, u'\u2717', u'\u2717']) 
                    config_not_defined.append(False)

        print ("\n{}: {} {}".format(config, len(k8s_object_list.items), k8s_object))
        Output.bar(config_not_defined,data, "container's running with no",k8s_object,config, Output.RED)
        Output.bar(liveness_probe,data, "container's running with",k8s_object,'liveness probe defined', Output.YELLOW)
        Output.bar(readiness_probe,data,"container's running with",k8s_object,'readiness probe defined', Output.YELLOW)
        Output.bar(both,data,"container's running with both",k8s_object,'liveness and readiness probe defined', Output.GREEN)
        return data

    def resources(k8s_object,k8s_object_list):
        data, config_not_defined, limits, requests, both = [], [], [], [], []
        config = 'resource limits/requests'      
        for item in k8s_object_list.items:
            k8s_object_name = item.metadata.name
            if 'pods' in k8s_object:
                containers = item.spec.containers
            else:
                containers = item.spec.template.spec.containers
            for container in containers:
                if container.resources.limits is not None and container.resources.requests is not None:
                    data.append([item.metadata.namespace, k8s_object_name, container.name, u'\u2714', u'\u2714'])
                    both.append(True)
                elif container.resources.limits is None and container.resources.requests is not None:
                    data.append([item.metadata.namespace, k8s_object_name, container.name, u'\u2717', u'\u2714'])
                    requests.append(True)
                elif container.resources.limits is not None and container.resources.requests is None:
                    data.append([item.metadata.namespace, k8s_object_name, container.name, u'\u2714', u'\u2717'])
                    limits.append(True)
                else:
                    data.append([item.metadata.namespace, k8s_object_name, container.name, u'\u2717', u'\u2717'])                
                    config_not_defined.append(False)
        print ("\n{}: {} {}".format(config, len(k8s_object_list.items), k8s_object))
        Output.bar(config_not_defined,data,"container's running without",k8s_object,config, Output.RED)
        Output.bar(requests,data,"container's running with",k8s_object,'requests defined', Output.YELLOW)
        Output.bar(limits,data,"container's running with",k8s_object,'limits defined', Output.YELLOW)
        Output.bar(both,data,"container's running with both",k8s_object,'limits and requests defined', Output.GREEN)
        return data

    def strategy(k8s_object,k8s_object_list):
        data = []        
        for item in k8s_object_list.items:
            k8s_object_name = item.metadata.name
            if item.spec.strategy is not None:
                data.append([item.metadata.name, item.spec.strategy.type])
        return data

    def replica(k8s_object,k8s_object_list):
        data, single_replica_count, config = [], [], 'replica'       
        for item in k8s_object_list.items:
            k8s_object_name = item.metadata.name
            if item.spec.replicas is not None:
                data.append([item.metadata.namespace, item.metadata.name, item.spec.replicas])
                if item.spec.replicas == 1:
                    single_replica_count.append(True)

        if len(single_replica_count) > 0:
            print ("\n{}: {} {}".format(config, len(k8s_object_list.items), k8s_object))
            Output.bar(single_replica_count, data, 'are running with 1', k8s_object, config, Output.RED)              
            return data

    #check for kube2iam
    def tolerations_affinity_node_selector_priority(k8s_object,k8s_object_list):
        data = []     
        affinity, node_selector, toleration = "", "", "" 
        for item in k8s_object_list.items:
            k8s_object_name = item.metadata.name
            if 'pods' in k8s_object:
                tolerations = item.spec.tolerations
                node_selectors = item.spec.node_selector
                affinitys = item.spec.affinity
                priority_class_name = item.spec.priority_class_name
            else:
                tolerations = item.spec.template.spec.tolerations
                node_selectors = item.spec.template.spec.node_selector
                affinitys = item.spec.template.spec.affinity
                priority_class_name = item.spec.template.spec.priority_class_name

            if tolerations is not None:
                toleration = u'\u2714'
            else:
                tolerations = u'\u2717'
            if node_selectors is not None:
                node_selector = u'\u2714'
            else:
                node_selector = u'\u2717'
            if affinitys is None:
                affinity = u'\u2717'
            elif affinitys.pod_anti_affinity is not None or \
                affinitys.pod_affinity is not None or \
                affinitys.node_affinity is not None:
                affinity = u'\u2714'
            else:
                affinity = u'\u2717'
            data.append([item.metadata.namespace, k8s_object_name, node_selector, \
            toleration, affinity, priority_class_name])  
        return data

    def qos(k8s_object,k8s_object_list):
        data, guaranteed, besteffort, burstable = [], [], [], []
        config = 'QoS'
        for item in k8s_object_list.items:
            data.append([item.metadata.namespace, item.metadata.name, item.status.qos_class])
            if 'Guaranteed' in item.status.qos_class:
                guaranteed.append([item.metadata.namespace, item.metadata.name])
            elif 'Burstable' in item.status.qos_class:
                burstable.append([item.metadata.namespace, item.metadata.name])
            else:
                besteffort.append([item.metadata.namespace, item.metadata.name])

        print ("\n{}: {} {}".format(config, len(k8s_object_list.items), k8s_object))
        Output.bar(guaranteed,data, 'is having Guaranteed', k8s_object, config, Output.GREEN)
        Output.bar(burstable,data, 'is having Burstable', k8s_object, config, Output.YELLOW)
        Output.bar(besteffort,data, 'is having BestEffort', k8s_object, config, Output.RED)

        return data

    def image_pull_policy(k8s_object,k8s_object_list):
        data, if_not_present, always, never= [], [], [], []
        config = 'image pull-policy'
        for item in k8s_object_list.items:
            if 'pods' in k8s_object:
                containers = item.spec.containers
            else:
                containers = item.spec.template.spec.containers            
            for container in containers:
                data.append([item.metadata.name, container.name, container.image, container.image_pull_policy])

        for image in data:
            if 'Always' in image[-1]:
                always.append(image[3])
            elif 'IfNotPresent' in image[-1]:
                if_not_present.append(True)
            else:
                never.append(True)  

        print ("\n{}: {} {}".format(config, len(k8s_object_list.items), k8s_object))            
        Output.bar(if_not_present, data, "container's with image pull-policy", k8s_object, '"IfNotPresent"', Output.YELLOW)
        Output.bar(always, data, "container's with image pull-policy", k8s_object, '"Always"', Output.GREEN)
        Output.bar(never, data, "container's with image pull-policy", k8s_object, '"Never"', Output.RED)
        return data 

class IngCheck:
    def get_ing_rules(ingress_rule,v):
        data = ""
        for i in ingress_rule:
            for j in i.http.paths:
                if i.host is None:
                    data = data + "-" + " [" + j.backend.service_name + ":" +  str(j.backend.service_port) + "]" + "\n"
                else:
                    data = data + i.host + " [" + j.backend.service_name + ":" +  str(j.backend.service_port) + "]" + "\n"
        return data

    def list_ingress(k8s_object_list,v):
        data = []
        for i in k8s_object_list.items:
            data.append([i.metadata.namespace, i.metadata.name, len(i.spec.rules), IngCheck.get_ing_rules(i.spec.rules,v)])
        return data      
    
class CtrlProp:
    def read_admission_controllers():
        admission_controllers_list = []
        with open('./conf/admission-controllers', "r") as file:
            admission_controllers_list = file.read()
        return admission_controllers_list

    def read_object_file(filename):
        object_args = []
        with open(filename, "r") as file:
            for line in file:
                object_args.append(line.split(None, 1)[0])
        return object_args

    def compare_properties(filename,commands):
        data, command_list = [], []
        object_args =  CtrlProp.read_object_file(filename)
        for c in commands:
            command = c.rsplit("=")[0]
            command_list.append(command)
            data.append([c, u'\u2714'])
        diff_list = list(set(object_args).difference(command_list))
        diff_list.sort()
        for i in diff_list:
            data.append([i, u'\u2717'])
        return data

    def check_admission_controllers(commands,v):
        admission_plugins_enabled, admission_plugins_not_enabled = [], []
        important_admission_plugins = ['AlwaysPullImages', 'DenyEscalatingExec',  \
        'LimitRange', 'NodeRestriction', 'PodSecurityPolicy', 'ResourceQuota', 'SecurityContextDeny']

        for c in commands:
            if 'enable-admission-plugins' in c:
                admission_plugins_enabled = (c.rsplit("=")[1]).split(",")
                print (Output.GREEN + "\nImportant Admission Controllers enabled: \n"+ \
                Output.RESET + "{}\n".format(admission_plugins_enabled))

                admission_plugins_list = CtrlProp.read_admission_controllers()

                admission_plugins_not_enabled = list(set(important_admission_plugins) - \
                set(admission_plugins_enabled))

                print (Output.RED + "Important Admission Controllers not enabled: \n" + \
                Output.RESET  + "{}\n".format(admission_plugins_not_enabled))

                if v: print (Output.YELLOW + "Admission Controllers available in k8s: \n" + \
                Output.RESET + "[{}]\n".format(admission_plugins_list))

    def secure_scheduler_check(commands):
        for c in commands:
            if '--address' in c and '--address=127.0.0.1' not in c:
                print (Output.RED + "[ALERT] " + Output.RESET + "Scheduler is not bound to a non-loopback insecure address \n")
            if c in '--profiling':
                print (Output.RED + "[ALERT] " + Output.RESET + "Disable profiling for reduced attack surface.\n")

class Service:
    def check_service(k8s_object, k8s_object_list):
        data, cluster_ip_svc, lb_svc, others_svc = [], [], [], []
        for item in k8s_object_list.items:
            if 'ClusterIP' in item.spec.type:
                cluster_ip_svc.append([item.metadata.namespace, item.metadata.name])
            elif 'LoadBalancer' in item.spec.type:
                lb_svc.append([item.metadata.namespace, item.metadata.name])
            else:
                others_svc.append([item.metadata.namespace, item.metadata.name])
        print ("\n{}: {} {}".format('service type: ', len(k8s_object_list.items), k8s_object))                
        Output.bar(cluster_ip_svc, k8s_object_list.items, 'out of ' + \
        str(len(k8s_object_list.items)) + ' services are of type', k8s_object, 'ClusterIP', Output.CYAN)
        Output.bar(lb_svc, k8s_object_list.items, 'out of ' + \
        str(len(k8s_object_list.items)) + ' services are of type', k8s_object, 'LoadBalancer', Output.CYAN)
        Output.bar(others_svc, k8s_object_list.items, 'out of ' + \
        str(len(k8s_object_list.items)) + ' services are of type', k8s_object, 'others', Output.RED)        

class Rbac:
    def get_rules(rules):
        data, api_groups, resources, verbs, rules_count = [], "", "", "", 0
        for i in rules:
            current_api_group = re.sub("[']", '', str(i.api_groups))
            if current_api_group != "":
                api_groups = api_groups + current_api_group + "\n"
            else:
                api_groups = api_groups +  "''" + "\n"
            resources = resources + re.sub("[']", '', str(i.resources)) + "\n"
            verbs = verbs + re.sub("[']", '', str(i.verbs)) + "\n"
            rules_count = rules_count + len(rules)
        data = [api_groups, resources, verbs, rules_count]
        return data

    def analyse_role(data,k8s_object):
        full_perm, delete_perm = [], []
        for i in data:
            if '*' in i[4]: full_perm.append([i[0]])
            if 'delete' in i[4]: delete_perm.append([i[0]])
        print ("\n{}: {}".format(k8s_object, len(data)))
        Output.bar(full_perm,data, 'are having full permission on selected', k8s_object, 'APIs', Output.RED)
        Output.bar(delete_perm,data,'are having delete permission on designated', k8s_object, 'APIs', Output.RED)         

class NameSpace:
    def get_ns_object_details(deployments,ds,sts,pods,svc,ingress,jobs,ns,ns_data):
        ns_deployments, ns_ds, ns_sts, ns_pods, ns_svc, ns_ing, ns_jobs = [], [], [], [], [], [], []
        for item in deployments.items:
            if item.metadata.namespace == ns:
                ns_deployments.append([item.metadata.namespace, item.metadata.name])
        for item in ds.items:
            if item.metadata.namespace == ns:
                ns_ds.append([item.metadata.namespace, item.metadata.name])
        for item in sts.items:
            if item.metadata.namespace == ns:
                ns_sts.append([item.metadata.namespace, item.metadata.name])
        for item in pods.items:
            if item.metadata.namespace == ns:
                ns_pods.append([item.metadata.namespace, item.metadata.name])
        for item in svc.items:
            if item.metadata.namespace == ns:
                ns_svc.append([item.metadata.namespace, item.metadata.name])            
        for item in ingress.items:
            if item.metadata.namespace == ns:
                ns_ing.append([item.metadata.namespace, item.metadata.name])
        for item in jobs.items:
            if item.metadata.namespace == ns:
                ns_jobs.append([item.metadata.namespace, item.metadata.name])
        ns_data.append([ns, len(ns_deployments), len(ns_ds), len(ns_sts), \
        len(ns_pods), len(ns_svc), len(ns_ing), len(ns_jobs)])

        return ns_data       

    def get_ns_details(ns_list,deployments,ds,sts,pods,svc,ingress,jobs):
        ns_data = []
        if type(ns_list) != str:
            for item in ns_list.items:
                ns = item.metadata.name     
                data = NameSpace.get_ns_object_details(deployments,ds,sts,pods,svc,ingress,jobs,ns,ns_data)
        else:
            ns = ns_list
            data = NameSpace.get_ns_object_details(deployments,ds,sts,pods,svc,ingress,jobs,ns,ns_data)
        return data

class Nodes:
    def get_latest_k8s_version(kubelet_version):
        ver = requests.get("https://storage.googleapis.com/kubernetes-release/release/stable.txt")
        latest_k8s_version = ver.text
        if version.parse(str(kubelet_version)) < version.parse(str(latest_k8s_version)):
            print(Output.YELLOW + "[WARNING] " + Output.RESET + \
            "Cluster is not running with latest kubernetes version: {}".format(latest_k8s_version))

    def get_latest_os_version(os):
        if 'Flatcar' in os:
            ver = requests.get("https://stable.release.flatcar-linux.net/amd64-usr/current/version.txt")
            latest_os_version = re.findall('(FLATCAR_VERSION=)(.+)', ver.text)
            current_os_version = os.split()[5]

            if version.parse(str(current_os_version)) < version.parse(str(latest_os_version[0][1])):
                print(Output.YELLOW + "[WARNING] " + Output.RESET + \
                "Cluster nodes are not running on latest {}{}".format(latest_os_version[0][0],latest_os_version[0][1]))
            return [ latest_os_version, current_os_version ]
        
    def get_latest_docker_version(docker_version):
        
        ver = requests.get("https://api.github.com/repositories/7691631/releases/latest")
        latest_docker_version = ver.json()['tag_name']
        if version.parse(str(docker_version)) < version.parse(str(latest_docker_version)):
            print(Output.YELLOW + "[WARNING] " + Output.RESET + \
            "Cluster nodes are not running on latest docker version: {}".format(latest_docker_version))