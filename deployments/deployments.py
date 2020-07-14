from kubernetes import client, config
from kubernetes.client.rest import ApiException
from pprint import pprint
from columnar import columnar
from click import style
import sys, time, os 
import datetime, pytz

start_time = time.time()
config.load_kube_config()
apps = client.AppsV1Api()

class Deployment:
    global patterns
    patterns = [('Yes', lambda text: style(text, fg='green')), \
                ('True', lambda text: style(text, fg='green')), \
                ('False', lambda text: style(text, fg='yellow'))]    

    def print_table(data,headers):
        table = columnar(data, headers, no_borders=True, patterns=patterns)
        print (table)        
        
    def get_deployments():
        try:
            namespace = 'kube-system'
            deployments = apps.list_namespaced_deployment(namespace, timeout_seconds=10)
            return deployments
        except ApiException as e:
            print("Exception when calling AppsV1Api->read_namespaced_deployment: %s\n" % e)

    def check_deployment_security():
        deployment_list = Deployment.get_deployments()
        data = []
        for deployment in deployment_list.items:
            headers = ['DEPLOYMENT', 'CONTAINER_NAME', 'PRIVILEGED_ESC', \
            'PRIVILEGED', 'READ_ONLY_FS', 'RUN_AS_NON_ROOT', 'RUNA_AS_USER']
            for container in deployment.spec.template.spec.containers:
                if container.security_context is not None:
                    data.append([deployment.metadata.name, container.name, \
                    container.security_context.allow_privilege_escalation, \
                    container.security_context.privileged,  \
                    container.security_context.read_only_root_filesystem, \
                    container.security_context.run_as_non_root, \
                    container.security_context.run_as_user ])   
                else:
                    data.append([deployment.metadata.name, container.name, \
                    'None', 'None', 'None', 'None', 'None'])  
        Deployment.print_table(data,headers)

    def check_deployment_health_probes():
        deployment_list = Deployment.get_deployments()
        data = []   
        last_deployment_name = ""
        for deployment in deployment_list.items:
            headers = ['DEPLOYMENT', 'CONTAINER_NAME', 'READINESS_PROPBE', 'LIVENESS_PROBE']
            for container in deployment.spec.template.spec.containers:
                if container.readiness_probe is not None and container.liveness_probe is not None:
                    data.append([deployment.metadata.name, container.name,'Yes', 'Yes'])  
                elif container.readiness_probe is None and container.liveness_probe is not None:
                    data.append([deployment.metadata.name, container.name, 'None', 'Yes'])  
                else:
                    data.append([deployment.metadata.name, container.name, 'Yes', 'None'])  
        Deployment.print_table(data,headers)

    def check_deployment_resources():
        deployment_list = Deployment.get_deployments()
        data = []   
        for deployment in deployment_list.items:
            headers = ['DEPLOYMENT', 'CONTAINER_NAME', 'LIMITS', 'REQUESTS']
            for container in deployment.spec.template.spec.containers:
                if container.resources.limits is not None and container.resources.requests is not None:
                    data.append([deployment.metadata.name, container.name,'Yes', 'Yes'])  
                else:
                    data.append([deployment.metadata.name, container.name, 'None', 'None'])  
        Deployment.print_table(data,headers)

    def check_deployment_strategy():
        deployment_list = Deployment.get_deployments()
        data = []   
        for deployment in deployment_list.items:
            headers = ['DEPLOYMENT', 'CONTAINER_NAME', 'STRATEGY_TYPE']
            deployment_name = deployment.metadata.name
            if deployment.spec.strategy is not None:
                data.append([deployment.metadata.name, deployment.spec.strategy.type])  
        Deployment.print_table(data,headers)   

    def check_deployment_tolerations_affinity_node_selector_priority():
        deployment_list = Deployment.get_deployments()
        data = []   
        for deployment in deployment_list.items:
            headers = ['DEPLOYMENT', 'NODE_SELECTOR', 'TOLERATIONS', 'AFFINITY', 'PRIORITY_CLASS']
            deployment_name = deployment.metadata.name
            if deployment.spec.template.spec.tolerations is not None:
                tolerations = 'Yes'
            if deployment.spec.template.spec.node_selector is not None:
                node_selector = 'Yes'
            if deployment.spec.template.spec.affinity is None:
                affinity = 'None'
            elif deployment.spec.template.spec.affinity.pod_anti_affinity is not None or \
                deployment.spec.template.spec.affinity.pod_affinity is not None or \
                deployment.spec.template.spec.affinity.node_affinity is not None:
                affinity = 'Yes'
            else:
                affinity = 'None'
            data.append([deployment.metadata.name, node_selector, tolerations, affinity, \
            deployment.spec.template.spec.priority_class_name])  
        Deployment.print_table(data,headers)      

def main():
    Deployment.check_deployment_security()
    Deployment.check_deployment_health_probes()
    Deployment.check_deployment_resources()
    Deployment.check_deployment_strategy()
    Deployment.check_deployment_tolerations_affinity_node_selector_priority()
    print("\033[1;30mTotal time taken:\033[0m %ss" % (time.time() - start_time))

if __name__ == "__main__":
    main()