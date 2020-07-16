from columnar import columnar
from click import style

class Output:
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    RESET = '\033[0m'  
    # u'\u2717' means values is None or not defined
    # u'\u2714' means value is defined
    global patterns
    patterns = [(u'\u2714', lambda text: style(text, fg='green')), \
                ('True', lambda text: style(text, fg='green')), \
                ('False', lambda text: style(text, fg='yellow'))]    

    def print_table(data,headers):
        table = columnar(data, headers, no_borders=True, patterns=patterns, row_sep='-')
        print (table)

    def percentage(config_not_defined,data,config):
        percentage = int((100.0 * len(config_not_defined) / len(data)))
        if percentage == 100:
            print (Output.YELLOW + "\n[WARNING] " + Output.RESET + "None of the deployments has defined {} for containers!".format(config))
        elif percentage == 0:
            print (Output.GREEN + "\n[OK] " + Output.RESET + "All deployments has defined {} for containers!".format(config))
        else:
            print (Output.YELLOW + "\n[WARNING] " + Output.RESET + "{}% of deployments has not defined {} for containers!".format(percentage, config))

class Check:
    def security_context(k8s_object,k8s_object_list):
        data, config_not_defined = [], []
        config = 'security context'
        for item in k8s_object_list.items:
            k8s_object_name = item.metadata.name
            for container in item.spec.template.spec.containers:
                if container.security_context is not None:
                    data.append([k8s_object_name, container.name, \
                    container.security_context.allow_privilege_escalation, \
                    container.security_context.privileged,  \
                    container.security_context.read_only_root_filesystem, \
                    container.security_context.run_as_non_root, \
                    container.security_context.run_as_user ])
                else:
                    data.append([k8s_object_name, container.name, \
                    u'\u2717', u'\u2717', u'\u2717', u'\u2717', u'\u2717'])  
                    config_not_defined.append(True)
        Output.percentage(config_not_defined,data,config)
        return data

    def health_probes(k8s_object,k8s_object_list):
        data, config_not_defined = [], []
        config = 'health checks'
        for item in k8s_object_list.items:
            k8s_object_name = item.metadata.name
            if k8s_object is 'pod':
                containers = item.spec.containers
            else:
                containers = item.spec.template.spec.containers
            for container in containers:
                if container.readiness_probe is not None and container.liveness_probe is not None:
                    data.append([k8s_object_name, container.name, u'\u2714', u'\u2714'])  
                elif container.readiness_probe is None and container.liveness_probe is not None:
                    data.append([k8s_object_name, container.name, u'\u2717', u'\u2714'])  
                elif container.readiness_probe is not None and container.liveness_probe is None:
                    data.append([item.metadata.name, container.name, u'\u2714', u'\u2717']) 
                else:
                    data.append([k8s_object_name, container.name, u'\u2717', u'\u2717']) 
                    config_not_defined.append(False)
        Output.percentage(config_not_defined,data,config)
        return data

    def resources(k8s_object,k8s_object_list):
        data, config_not_defined = [], []
        config = 'resource limits/requests'      
        for item in k8s_object_list.items:
            k8s_object_name = item.metadata.name
            if k8s_object is 'pod':
                containers = item.spec.containers
            else:
                containers = item.spec.template.spec.containers
            for container in containers:
                if container.resources.limits is not None and container.resources.requests is not None:
                    data.append([k8s_object_name, container.name, u'\u2714', u'\u2714'])  
                elif container.resources.limits is None and container.resources.requests is not None:
                    data.append([k8s_object_name, container.name, u'\u2717', u'\u2714'])
                elif container.resources.limits is not None and container.resources.requests is None:
                    data.append([k8s_object_name, container.name, u'\u2714', u'\u2717'])
                else:
                    data.append([k8s_object_name, container.name, u'\u2717', u'\u2717'])                
                    config_not_defined.append(False)
        Output.percentage(config_not_defined,data,config)
        return data

    def strategy(k8s_object,k8s_object_list):
        data = []        
        for item in k8s_object_list.items:
            k8s_object_name = item.metadata.name
            if item.spec.strategy is not None:
                data.append([item.metadata.name, item.spec.strategy.type])
        return data

    def tolerations_affinity_node_selector_priority(k8s_object,k8s_object_list):
        data = []     
        affinity, node_selector, tolerations = "", "", ""                  
        for item in k8s_object_list.items:
            k8s_object_name = item.metadata.name
            if item.spec.template.spec.tolerations is not None:
                tolerations = u'\u2714'
            else:
                tolerations = u'\u2717'
            if item.spec.template.spec.node_selector is not None:
                node_selector = u'\u2714'
            else:
                node_selector = u'\u2717'
            if item.spec.template.spec.affinity is None:
                affinity = u'\u2717'
            elif item.spec.template.spec.affinity.pod_anti_affinity is not None or \
                item.spec.template.spec.affinity.pod_affinity is not None or \
                item.spec.template.spec.affinity.node_affinity is not None:
                affinity = u'\u2714'
            else:
                affinity = u'\u2717'
            data.append([k8s_object_name, node_selector, tolerations, affinity, \
            item.spec.template.spec.priority_class_name])  
        return data

class CtrlProp:
    def compare_properties(filename,obj_name,commands):
        object_args, data, command_list = [], [], []
        with open(filename, "r") as file:
            for line in file:
                object_args.append(line.split(None, 1)[0])                
        # for args in object_args:
        for c in commands:
            command = c.rsplit("=")[0]
            command_list.append(command)
            data.append([command, u'\u2714'])
        #         if command == args:
        #             data.append([command, u'\u2714'])
        #             check = True
        #             break
        new_list = list(set(object_args).difference(command_list))
        for i in new_list:
            data.append([i, u'\u2717'])
        return data