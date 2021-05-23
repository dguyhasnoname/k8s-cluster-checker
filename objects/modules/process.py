from packaging import version
import os, re, time, requests, json, csv
#from .logging import Logger
from .output import Output

# global logger
# logger = Logger.get_logger('', '')


class Check:  
    # check security context
    def security_context(k8s_object, k8s_object_list, headers, v, ns, l, logger):
        data, config_not_defined, privileged_containers, run_as_user, \
        allow_privilege_escalation, read_only_root_filesystem, \
        run_as_non_root = [], [], [], [], [], [], []
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
                    if container.security_context.privileged:
                        privileged_containers.append(True)
                    if container.security_context.run_as_user:
                        run_as_user.append(True)
                    if container.security_context.allow_privilege_escalation:
                        allow_privilege_escalation.append(True)
                    if container.security_context.read_only_root_filesystem:
                        read_only_root_filesystem.append(True)
                    if container.security_context.run_as_non_root:
                        run_as_non_root.append(True)
                else:
                    data.append([item.metadata.namespace, k8s_object_name, container.name, \
                    u'\u2717', u'\u2717', u'\u2717', u'\u2717', u'\u2717'])
                    config_not_defined.append(True)

        print ("\nsecurity_context definition: {} {}".format(len(k8s_object_list.items), \
        k8s_object))
        data_no_sec_context = Output.bar(config_not_defined, data, \
        "containers have no security_context defined in running", \
        k8s_object, Output.RED, l, logger)
        data_privileged = Output.bar(privileged_containers, data, \
        'containers are in prvilleged mode in running', k8s_object, Output.RED, l, logger)
        data_allow_privilege_escalation = Output.bar(allow_privilege_escalation, data, \
        'containers found in allow_privilege_escalation mode in running', \
        k8s_object, Output.RED, l, logger)
        data_run_as_user = Output.bar(run_as_user, data, \
        "containers have some user defined in running", 
        k8s_object, Output.GREEN, l, logger)
        data_run_as_non_root = Output.bar(run_as_non_root, data, \
        "containers are having non_root_user in running", k8s_object, Output.GREEN, l, logger)
        data_read_only_root_filesystem = Output.bar(read_only_root_filesystem, data, \
        "containers only have read-only root filesystem in all running", \
        k8s_object, Output.GREEN, l, logger)
        Output.print_table(data, headers, v, l)
        Output.csv_out(data, headers, k8s_object, 'security_context', ns)  

        # creating analysis data for logging
        analysis = {"container_property": "security_context",
                    "total_container_count": len(data),
                    "no_security_context_defined_containers": data_no_sec_context,
                    "privileged_containers": data_privileged,
                    "allow_privilege_escalation_containers": data_allow_privilege_escalation,
                    "run_as_user": data_run_as_user,
                    "read_only_root_filesystem_containers": data_read_only_root_filesystem}
        json_data = Output.json_out(data, analysis, headers, k8s_object, 'security_context', ns)

        return json_data

    # check health probes defined
    def health_probes(k8s_object, k8s_object_list, headers, v, ns, l, logger):
        data, config_not_defined, readiness_probe, liveness_probe, both = \
        [], [], [], [], []
        for item in k8s_object_list.items:
            k8s_object_name = item.metadata.name
            if 'pods' in k8s_object:
                containers = item.spec.containers
            else:
                containers = item.spec.template.spec.containers
            for container in containers:
                if container.readiness_probe is not None and \
                container.liveness_probe is not None:
                    data.append([item.metadata.namespace, k8s_object_name, \
                    container.name, u'\u2714', u'\u2714'])
                    both.append(True)
                elif container.readiness_probe is None and \
                container.liveness_probe is not None:
                    data.append([item.metadata.namespace, k8s_object_name, \
                    container.name, u'\u2717', u'\u2714'])
                    liveness_probe.append(True)
                elif container.readiness_probe is not None and \
                container.liveness_probe is None:
                    data.append([item.metadata.namespace, k8s_object_name, \
                    container.name, u'\u2714', u'\u2717'])
                    readiness_probe.append(True)
                else:
                    data.append([item.metadata.namespace, k8s_object_name, \
                    container.name, u'\u2717', u'\u2717'])
                    config_not_defined.append(False)

        logger.info ("health_probes definition: {} {}"\
        .format(len(k8s_object_list.items), k8s_object))
        data_no_health_probes = Output.bar(config_not_defined,data, \
        "containers found with no health probes in running", \
        k8s_object, Output.RED, l, logger)
        data_livness_probe = Output.bar(liveness_probe, data, \
        "containers found with only liveness probe defined in running", \
        k8s_object, Output.YELLOW, l, logger)
        data_readiness_probe = Output.bar(readiness_probe, data, \
        "containers found with only readiness probe defined in running", \
        k8s_object, Output.YELLOW, l, logger)
        data_all_probe = Output.bar(both, data, \
        "containers found having both liveness and readiness probe defined in running", 
        k8s_object, Output.GREEN, l, logger)
        Output.print_table(data, headers, v, l)
        Output.csv_out(data, headers, k8s_object, 'health_probes', ns)

        # creating analysis data for logging
        analysis = {"container_property": "health_probes",
                    "total_container_count": len(data),
                    "no_health_probes_defined_containers": data_no_health_probes,
                    "only_liveness_probe_defined_containers": data_livness_probe,
                    "only_readiness_probe_defined_containers": data_readiness_probe,
                    "all_probes_defined_containers": data_all_probe}        
        json_data = Output.json_out(data, analysis, headers, k8s_object, 'health_probes', ns)    

        return json_data

    # check resource requests/limits
    def resources(k8s_object, k8s_object_list, headers, v, ns, l, logger):
        data, config_not_defined, limits, requests, both = [], [], [], [], []
        for item in k8s_object_list.items:
            k8s_object_name = item.metadata.name
            if 'pods' in k8s_object:
                containers = item.spec.containers
            else:
                containers = item.spec.template.spec.containers
            for container in containers:
                if container.resources.limits is not None and \
                container.resources.requests is not None:
                    data.append([item.metadata.namespace, k8s_object_name, \
                    container.name, u'\u2714', u'\u2714'])
                    both.append(True)
                elif container.resources.limits is None and \
                container.resources.requests is not None:
                    data.append([item.metadata.namespace, k8s_object_name, \
                    container.name, u'\u2717', u'\u2714'])
                    requests.append(True)
                elif container.resources.limits is not None and \
                container.resources.requests is None:
                    data.append([item.metadata.namespace, k8s_object_name, \
                    container.name, u'\u2714', u'\u2717'])
                    limits.append(True)
                else:
                    data.append([item.metadata.namespace, k8s_object_name, \
                    container.name, u'\u2717', u'\u2717'])
                    config_not_defined.append(False)
        logger.info ("resource definition: {} {}".format(len(k8s_object_list.items), \
        k8s_object))
        data_no_resources = Output.bar(config_not_defined,data, \
        "containers found without resources defined in running", \
        k8s_object, Output.RED, l, logger)
        data_requests = Output.bar(requests,data, \
        "containers found with only requests defined in running", 
        k8s_object, Output.YELLOW, l, logger)
        data_limits = Output.bar(limits,data, \
        "containers found with only limits defined in running", \
        k8s_object, Output.YELLOW, l, logger)
        data_all = Output.bar(both,data, \
        "containers found with both limits and requests defined in running", \
        k8s_object, Output.GREEN, l, logger)
        Output.print_table(data, headers, v, l)
        Output.csv_out(data, headers, k8s_object, 'resource_definition', ns)

        # creating analysis data for logging
        analysis = {"container_property": "resources",
                    "total_container_count": len(data),
                    "no_resources_defined_containers": data_no_resources,
                    "only_limits_defined_containers": data_limits,
                    "only_requests_defined_containers": data_requests,
                    "all_resources_defined_containers": data_all}                
        json_data = Output.json_out(data, analysis, headers, k8s_object, 'resource_definition', ns)  

        return json_data

    # check for rollout strategy
    def strategy(k8s_object, k8s_object_list, headers, v, ns, l, logger):
        data = []
        for item in k8s_object_list.items:
            k8s_object_name = item.metadata.name
            if item.spec.strategy is not None:
                data.append([item.metadata.name, item.spec.strategy.type])
        Output.print_table(data, headers, v, l)
        Output.csv_out(data, headers, k8s_object, 'rollout_strategy', ns)
        json_data = Output.json_out(data, '', headers, k8s_object, 'rollout_strategy', ns)
        return json_data

    # check for single replica
    def replica(k8s_object, k8s_object_list, headers, v, ns, l, logger):
        data, single_replica_count, multi_replica_count = [], [], []
        for item in k8s_object_list.items:
            k8s_object_name = item.metadata.name
            if item.spec.replicas is not None:
                data.append([item.metadata.namespace, item.metadata.name, \
                item.spec.replicas])
                if item.spec.replicas == 1:
                    single_replica_count.append(True)
                else:
                    multi_replica_count.append(True)

        if len(single_replica_count) > 0:
            logger.info ("single replica check: {} {}".format(len(k8s_object_list.items), \
            k8s_object))
            data_single_replica = Output.bar(single_replica_count, data, str(k8s_object) + \
            ' are running with 1 replica in all', k8s_object, Output.RED, l, logger)
            Output.print_table(data, headers, v, l)
            Output.csv_out(data, headers, k8s_object, 'single_replica_deployment', ns)

            # creating analysis data for logging
            analysis = {"deployment_property": "single_relica",
                        "total_deployment_count": len(data),
                        "single_replica_deployment_count": data_single_replica}

            json_data = Output.json_out(data, analysis, headers, k8s_object, 'single_replica_deployment', ns)        
            return json_data
        return data

    def tolerations_affinity_node_selector_priority(k8s_object, k8s_object_list, headers, v, ns, l, logger):
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
            data.append([item.metadata.namespace, k8s_object_name, \
            node_selector, toleration, affinity, priority_class_name])
        if v or l: print ("\ntolerations_affinity_node_selector_priority check: {} {}"\
        .format(len(k8s_object_list.items), k8s_object))            
        Output.print_table(data, headers, v, l)
        Output.csv_out(data, headers, k8s_object, \
        'tolerations_affinity_node_selector_priority', ns)
        json_data = Output.json_out(data, '',headers, k8s_object, \
        'tolerations_affinity_node_selector_priority', ns)  

        return json_data

    def qos(k8s_object, k8s_object_list, headers, v, ns, l, logger):
        data, guaranteed, besteffort, burstable = [], [], [], []
        if not k8s_object_list: return
        for item in k8s_object_list.items:
            data.append([item.metadata.namespace, item.metadata.name, \
            item.status.qos_class])
            if 'Guaranteed' in item.status.qos_class:
                guaranteed.append([item.metadata.namespace, item.metadata.name])
            elif 'Burstable' in item.status.qos_class:
                burstable.append([item.metadata.namespace, item.metadata.name])
            else:
                besteffort.append([item.metadata.namespace, item.metadata.name])

        logger.info ("QoS check: {} {}".format(len(k8s_object_list.items), \
        k8s_object))
        data_guaranteed = Output.bar(guaranteed, data, str(k8s_object) + \
        ' are having Guaranteed QoS out of all', k8s_object, Output.GREEN, l, logger)
        data_burstable = Output.bar(burstable, data, str(k8s_object) + \
        ' are having Burstable QoS out of all', k8s_object, Output.YELLOW, l, logger)
        data_besteffort = Output.bar(besteffort, data, str(k8s_object) + \
        ' are having BestEffort QoS out of all', k8s_object, Output.RED, l, logger)
        Output.print_table(data, headers, v, l)
        Output.csv_out(data, headers, k8s_object, 'QoS', ns)

        # creating analysis data for logging
        analysis = {"container_property": "qos",
                    "total_pods_count": len(data),
                    "guaranteed_pods_count": data_guaranteed,
                    "burstable_pods_count": data_burstable,
                    "besteffort_pods_count": data_besteffort}          
        json_data = Output.json_out(data, analysis, headers, k8s_object, 'QoS', ns)

        return json_data

    def image_pull_policy(k8s_object, k8s_object_list, headers, v, ns, l, logger):
        data, if_not_present, always, never= [], [], [], []
        config = 'image pull-policy'
        for item in k8s_object_list.items:
            if 'pods' in k8s_object:
                containers = item.spec.containers
            else:
                containers = item.spec.template.spec.containers
            for container in containers:
                data.append([item.metadata.name, container.name, \
                container.image, container.image_pull_policy])

        for image in data:
            if 'Always' in image[-1]:
                always.append(image[3])
            elif 'IfNotPresent' in image[-1]:
                if_not_present.append(True)
            else:
                never.append(True)

        print ("\n{}: {} {}".format(config, len(k8s_object_list.items), \
        k8s_object))        
        data_if_not_present = Output.bar(if_not_present, data, \
        'containers have "IfNotPresent" image pull-policy in all', \
        k8s_object, Output.YELLOW, l, logger)
        data_always = Output.bar(always, data, \
        'containers have "Always" image pull-policy in all', \
        k8s_object, Output.GREEN, l, logger)
        data_never = Output.bar(never, data, \
        'containers have "Never" image pull-policy in all', \
        k8s_object, Output.RED, l, logger)
        Output.print_table(data, headers, v ,l)
        Output.csv_out(data, headers, k8s_object, 'image_pull_policy', ns)

        # creating analysis data for logging
        analysis = {"container_property": "image_pull_policy",
                    "total_containers_count": len(data),
                    "if_not_present_pull_policy_containers_count": data_if_not_present,
                    "always_pull_policy_containers_count": data_always,
                    "never_pull_policy_containers_count": data_never}         
        json_data = Output.json_out(data, analysis, headers, k8s_object, 'image_pull_policy', ns)    

        return json_data

class IngCheck:
    # checking mapping of ingress
    def get_ing_rules(ingress_rule, v):
        data = ""
        for i in ingress_rule:
            for j in i.http.paths:
                if i.host is None:
                    data = data + "-" + " [" + j.backend.service_name + ":" +  \
                    str(j.backend.service_port) + "]" + "\n"
                else:
                    data = data + i.host + " [" + j.backend.service_name + ":" \
                    +  str(j.backend.service_port) + "]" + "\n"
        return data

    def list_ingress(k8s_object_list, k8s_object, headers, v, ns , l):
        data, total_rules_count = [], 0
        for i in k8s_object_list.items:
            data.append([i.metadata.namespace, i.metadata.name, \
            len(i.spec.rules), IngCheck.get_ing_rules(i.spec.rules,v)])
            total_rules_count += len(i.spec.rules)
        Output.print_table(data, headers, v, l)
        Output.csv_out(data, headers, k8s_object, 'ingress', ns)

        # creating analysis data for logging
        analysis = {"ingress_property": "ingress_rules",
                    "total_ingress_count": len(data),
                    "total_ingress_rules": total_rules_count
                    } 
        json_data = Output.json_out(data, analysis, headers, k8s_object, 'ingress', ns)    
        if l: logger.info(json_data)

        return json_data

class CtrlProp:
    def read_admission_controllers():
        admission_controllers_list = []
        with open('./conf/admission-controllers', "r") as file:
            admission_controllers_list = file.read()
        return admission_controllers_list

    # read property file from conf dir, file name being passed from compare_properties function
    def read_object_file(filename):
        object_args = []
        with open(filename, "r") as file:
            for line in file:
                object_args.append(line.split(None, 1)[0])
        return object_args

    # gets file name from check_ctrl_plane_pods_properties_operation function in ctrl-plane.py
    def compare_properties(filename, commands):
        data, command_list = [], []
        object_args =  CtrlProp.read_object_file(filename)
        for c in commands:
            command = c.rsplit("=")[0]
            command_list.append(command)
            data.append([c, u'\u2714'])
        # compares the properties in conf file and commands args set in ctrl pods
        diff_list = list(set(object_args).difference(command_list))
        diff_list.sort()
        for i in diff_list:
            data.append([i, u'\u2717'])
        return data

    def check_admission_controllers(commands, v, ns, l):
        data, admission_plugins_enabled, admission_plugins_not_enabled, \
        headers = [], [], [], ['ADMISSION_PLUGINS', 'ENABLED']
        important_admission_plugins = ['AlwaysPullImages', \
        'DenyEscalatingExec', 'LimitRange', 'NodeRestriction', \
        'PodSecurityPolicy', 'ResourceQuota', 'SecurityContextDeny']

        # checking which addmission controllers are enabled
        for c in commands:
            if 'enable-admission-plugins' in c:
                admission_plugins_enabled = (c.rsplit("=")[1]).split(",")
                for i in admission_plugins_enabled:
                    data.append([i, u'\u2714'])
                admission_plugins_list = CtrlProp.read_admission_controllers()

                # checking difference in addmission controllers
                admission_plugins_not_enabled = list(set(important_admission_plugins) - \
                set(admission_plugins_enabled))

                for i in admission_plugins_not_enabled:
                    data.append([i, u'\u2717'])

                if v:
                    # converting string admission_plugins_list into list and looping over
                    for i in admission_plugins_list.split(", "):
                        data.append([i, u'\u2717'])
                if not v: print ("\nStatus of important admission controllers:")
                Output.print_table(data, headers, True, l)
                Output.csv_out(data, headers, 'admission_controllers', '', ns)

                analysis = {"ctrl_plane_property": "admission_controllers_status",
                            "admission_plugins_enabled_count": len(admission_plugins_enabled),
                            "admission_plugins_enabled": admission_plugins_enabled,
                            "admission_plugins_not_enabled_count": len(admission_plugins_not_enabled),
                            "admission_plugins_not_enabled": admission_plugins_not_enabled,
                            "admission_plugins_available": admission_plugins_list
                            }
                json_data = Output.json_out(data, analysis, headers, 'admission_controllers', '', ns)

                return json_data

    def secure_scheduler_check(commands):
        for c in commands:
            if '--address' in c and '--address=127.0.0.1' not in c:
                print (Output.RED + "[ALERT] " + Output.RESET + \
                "Scheduler is not bound to a non-loopback insecure address \n")
            if c in '--profiling':
                print (Output.RED + "[ALERT] " + Output.RESET + \
                "Disable profiling for reduced attack surface.\n")

class Service:   
    # checking type of services
    def check_service(k8s_object, k8s_object_list, l, logger):
        cluster_ip_svc, lb_svc, others_svc = [], [], []
        for item in k8s_object_list.items:
            if 'ClusterIP' in item.spec.type:
                cluster_ip_svc.append([item.metadata.namespace, item.metadata.name])
            elif 'LoadBalancer' in item.spec.type:
                lb_svc.append([item.metadata.namespace, item.metadata.name])
            else:
                others_svc.append([item.metadata.namespace, item.metadata.name])
        print ("\n{}: {} {}".format('service type: ', \
        len(k8s_object_list.items), k8s_object))    
        data_cluster_ip = Output.bar(cluster_ip_svc, k8s_object_list.items, \
        'ClusterIP type', k8s_object, Output.CYAN, l, logger)
        data_lb = Output.bar(lb_svc, k8s_object_list.items, \
        'LoadBalancer type', k8s_object, Output.CYAN, l, logger)
        data_others = Output.bar(others_svc, k8s_object_list.items, \
        'others type', k8s_object, Output.RED, l, logger)

        return [data_cluster_ip, data_lb, data_others]

    def get_service(k8s_object, k8s_object_list, headers, v, ns, l, logger):
        data = []
        for item in k8s_object_list.items:
            if item.spec.selector:
                for i in item.spec.selector:
                    app_label = i
                    break
                data.append([item.metadata.namespace, item.metadata.name, item.spec.type, \
                item.spec.cluster_ip, app_label + ": " + item.spec.selector[app_label]])
            else:
                data.append([item.metadata.namespace, item.metadata.name, item.spec.type, \
                item.spec.cluster_ip, "None"])
        analysis = Service.check_service(k8s_object, k8s_object_list, l, logger)
        Output.csv_out(data, headers, k8s_object, 'service', ns)
        
        # creating analysis data for logging
        analysis = {"service_property": "service_type",
                    "total_service_count": len(data),
                    "cluster_ip_type_count": analysis[0],
                    "lb_type_count": analysis[1],
                    "others_type_count": analysis[2]
                    }
        json_data = Output.json_out(data, analysis, headers, k8s_object, 'service', ns)    
        if l: logger.info(json_data)
        return [json_data, data] 

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

    # analysis RBAC for permissions
    def analyse_role(data, headers, k8s_object, ns, l, logger):
        full_perm, full_perm_list, full_perm_list_json, delete_perm, \
        impersonate_perm, exec_perm = [], [], [], [], [], []
        data_api_specific_delete_perm, data_impersonate_perm, \
        data_full_delete_perm, data_exec_perm = '', '', '', ''
        for i in data:
            if '*' in i[-1] and '*' in i[-2] and '*' in i[-3]:
                full_perm.append([i[0]])
                # creating data for roles with full permissions on all resources and apigroups
                if  k8s_object == 'roles':
                    full_perm_list.append([i[0], i[1], i[2], i[3], i[4], i[5]])
                    full_perm_list_json.append({"role_name": i[0],
                                                "namespace": i[1],
                                                "api_groups": i[3].strip('\n'),
                                                "resources": i[4].strip('\n'),
                                                "verbs": i[5].strip('\n')
                                                })
                # creating separate data(due to difference in columns) for clusterroles with full permissions on all resources and apigroups
                else:
                    full_perm_list.append([i[0], i[1], i[2], i[3], i[4]])
                    full_perm_list_json.append({"cluster_role_name": i[0],
                                                "api_groups": i[2].strip('\n'),
                                                "resources": i[3].strip('\n'),
                                                "verbs": i[4].strip('\n')
                                                })
            if 'delete' in i[-1] and '*' in i[-2]: delete_perm.append([i[0]])
            if 'impersonate' in i[4]: impersonate_perm.append([i[0]])
            if 'exec' in i[-2]: exec_perm.append([i[0]])

        print ("\n{}: {}".format(k8s_object, len(data)))
        if len(full_perm):
            data_full_delete_perm = Output.bar(full_perm, data, \
            'full permission(on ALL RESOURCES and APIs) ' \
            + Output.RED + u'\u2620' + u'\u2620' + u'\u2620' + Output.RESET, \
            k8s_object, Output.RED, l, logger)
            Output.print_table(full_perm_list, headers, True, l)
        else:
            print (Output.GREEN + "[OK] " + Output.RESET + \
            "No {} full permission ".format(k8s_object))
        if len(delete_perm):
            data_api_specific_delete_perm = Output.bar(delete_perm, data, \
            'delete permission(on ALL RESOURCES on specfic APIs)', \
            k8s_object, Output.RED, l, logger)
        if len(impersonate_perm):
            data_impersonate_perm = Output.bar(impersonate_perm, data, \
            'impersonate permission(on specfic APIs)', \
            k8s_object, Output.RED, l, logger)
        if len(exec_perm):
            data_exec_perm = Output.bar(exec_perm, data, \
            'exec permission(on pods)', \
            k8s_object, Output.RED, l, logger)
        Output.csv_out(data, headers, 'rbac', k8s_object, ns)

        # creating analysis data for logging
        analysis = {"rbac_type": k8s_object,
                    "total_rbac_type_count": len(data),
                    "full_delete_perm_role": data_full_delete_perm,
                    "full_permission_role_list": full_perm_list_json,
                    "api_specific_delete_perm_role": data_api_specific_delete_perm,
                    "impersonate_perm_role": data_impersonate_perm,
                    "exec_perm_role": data_exec_perm
                    }
        json_data = Output.json_out(data, analysis, headers, 'rbac', k8s_object, ns)
        if l: logger.info(json_data)
        return json_data        

class NameSpace:
    #calculating count for a speific object in a namespace
    def get_ns_object_details(deployments, ds, sts, pods, svc, ingress, jobs,\
     roles, role_bindings, ns, ns_data):
        ns_deployments, ns_ds, ns_sts, ns_pods, ns_svc, ns_ing, \
        ns_jobs, ns_roles, ns_role_bindings = \
        [], [], [], [], [], [], [], [], []
        for item in deployments.items:
            if item.metadata.namespace == ns:
                ns_deployments.append([item.metadata.namespace, \
                item.metadata.name])
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
        if ingress:
            for item in ingress.items:
                if item.metadata.namespace == ns:
                    ns_ing.append([item.metadata.namespace, item.metadata.name])
        for item in jobs.items:
            if item.metadata.namespace == ns:
                ns_jobs.append([item.metadata.namespace, item.metadata.name])
        for item in roles.items:
            if item.metadata.namespace == ns:
                ns_roles.append([item.metadata.namespace, item.metadata.name])
        for item in role_bindings.items:
            if item.metadata.namespace == ns:
                ns_role_bindings.append([item.metadata.namespace, \
                item.metadata.name])  
        ns_data.append([ns, len(ns_deployments), len(ns_ds), len(ns_sts), \
        len(ns_pods), len(ns_svc), len(ns_ing), len(ns_jobs), len(ns_roles), \
        len(ns_role_bindings)])

        return ns_data

    # calculating count of different objects type in all namespaces
    def get_ns_details(ns_list, deployments, ds, sts, pods, svc, ingress, \
    jobs, roles, role_bindings):
        ns_data = []
        if type(ns_list) != str:
            for item in ns_list.items:
                ns = item.metadata.name 
                data = NameSpace.get_ns_object_details(deployments, ds, sts,\
                 pods, svc, ingress, jobs, roles, role_bindings, ns, ns_data)
        else:
            ns = ns_list
            data = NameSpace.get_ns_object_details(deployments, ds, sts, \
            pods, svc, ingress, jobs, roles, role_bindings, ns, ns_data)
        return data

class Nodes:
    global version_check
    version_check = []
    outdated = Output.RED +  'outdated' + Output.RESET
    latest = Output.GREEN +  'latest' + Output.RESET    
    # checking latest k8s version and comparing it with installed k8s version
    def get_latest_k8s_version(kubelet_version, logger):
        session = requests.Session()
        ver = requests.get("https://storage.googleapis.com/kubernetes-release/release/stable.txt")
        session.close()
        latest_k8s_version = ver.text
        if version.parse(str(kubelet_version)) < version.parse(str(latest_k8s_version)):
            logger.warning("Cluster is not running with latest kubernetes version: {}"\
                        .format(latest_k8s_version))
            status = Nodes.outdated
        else:
            status = Nodes.latest

        return version_check.append(['K8S', latest_k8s_version, kubelet_version, status])

    # checking latest OS version and comparing it with installed OS version
    def get_latest_os_version(os, logger):
        latest_os_version, current_os_version, status = [''] * 3
        if 'Flatcar' in os:
            session = requests.Session()
            ver = session.get("https://stable.release.flatcar-linux.net/amd64-usr/current/version.txt")
            session.close()
            latest_os_version = re.findall('(FLATCAR_VERSION=)(.+)', ver.text)
            current_os_version = os.split()[5]

            if version.parse(str(current_os_version)) < version.parse(str(latest_os_version[0][1])):
                logger.warning("Cluster nodes are not running on latest {}{}"\
                        .format(latest_os_version[0][0], latest_os_version[0][1]))
                status = Nodes.outdated
                latest_os_version = latest_os_version[0][1]
            else:
                status = Nodes.latest
                latest_os_version = latest_os_version[0][1]

        elif 'CoreOS' in os:
            logger.warning("Cluster nodes are running on CoreOS which is DPERECATED: https://coreos.com/os/eol/. " + \
            "PLEASE CONSIDER CHANGING THE DEPRECATED OS!")
            latest_os_version = 'EOL'
            status = 'EOL'
        elif 'Ubuntu' in os:
            current_os_version = re.sub('[^0-9.]','', os)
            session = requests.Session()
            ver = requests.get("https://api.launchpad.net/devel/ubuntu/series")
            session.close()
            for x in ver.json()['entries']:
                if 'Current Stable Release' in x['status']:
                    latest_os_version = x['version']
                    if version.parse(str(current_os_version)) < version.parse(str(latest_os_version)):
                        logger.warning("Cluster nodes are not running on latest Ubuntu version.")
                        status = Nodes.outdated
                    else:
                        status = Nodes.latest
        else:
            latest_os_version, current_os_version, status = ['OS not supported'] * 3

        return version_check.append(['OS', latest_os_version, current_os_version, status])

    # checking latest docker version and comparing it with installed docker version
    def get_latest_docker_version(docker_version, logger):
        ver = requests.get("https://api.github.com/repositories/7691631/releases/latest")
        latest_docker_version = ver.json()['tag_name']
        if version.parse(str(docker_version)) < version.parse(str(latest_docker_version)):
            logger.warning("Cluster nodes are not running on latest docker version: {}"\
            .format(latest_docker_version))
            status =  Nodes.outdated
        else:
            status = Nodes.latest

        return version_check.append(['DOCKER', latest_docker_version, docker_version, status])

    def node_version_check(current_os_version, docker_version, kubelet_version, l, logger):
        headers, outdated_nodes = ['COMPONENT', 'LATEST_VERSION', 'INSTALLED_VERSION', 'STATUS'], []
        Nodes.get_latest_os_version(current_os_version, logger)
        Nodes.get_latest_docker_version(docker_version, logger)
        Nodes.get_latest_k8s_version(kubelet_version, logger)
        for i in version_check:
            if i[3] in ['outdated', 'EOL']:
                outdated_nodes.append(True)
        data_outdated = Output.bar(outdated_nodes, version_check, \
        'version checks reported as', 'outdated', Output.RED, l, logger)
        Output.print_table(version_check, headers, True, l)
        Output.csv_out(version_check, headers, 'node', 'version', '')

        # creating analysis report
        analysis = {"node_property": "version",
                    "total_version_check": len(version_check),
                    "outdated_version_components": data_outdated
                    }
        json_data = Output.json_out(version_check, analysis, headers, 'node', 'version', '')

        return json_data

class CRDs:
    def check_ns_crd(k8s_object_list, k8s_object, data, headers, v, ns, l, logger):
        ns_crds, cluster_crds, other_crds = [], [], []
        for item in k8s_object_list.items:
            if 'Namespaced' in item.spec.scope:
                ns_crds.append([item.spec.group, item.metadata.name, \
                item.spec.scope])
            elif 'Cluster' in item.spec.scope:
                cluster_crds.append([item.spec.group, item.metadata.name, \
                item.spec.scope])
            else:
                other_crds.append([item.spec.group, item.metadata.name, \
                item.spec.scope])
        data_ns_scope = Output.bar(ns_crds, k8s_object_list.items, \
        'Namespaced scope', k8s_object, Output.CYAN, l, logger)
        data_cluster_scope = Output.bar(cluster_crds, k8s_object_list.items, \
        'Cluster scope', k8s_object, Output.CYAN, l, logger)
        data_cluster_scope = Output.bar(other_crds, k8s_object_list.items, \
        'Other scope', k8s_object, Output.CYAN, l, logger)   

        Output.print_table(data, headers, v, l)
        Output.csv_out(data, headers, k8s_object, '', ns)

        # creating analysis data for logging
        analysis = {"crd_property": "crd_scope",
                    "total_crd_count": len(data),
                    "namespace_scope_crd_count": data_ns_scope,
                    "cluster_scope_crd_count": data_cluster_scope,
                    "other_scope_crd_count": data_cluster_scope
                    }
        json_data = Output.json_out(data, analysis, headers, k8s_object, '', ns)
        if l: logger.info(json_data)
        return json_data