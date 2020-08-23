import sys, time, os, re, getopt
import requests
start_time = time.time()
from modules.main import GetOpts
from modules import logging as logger
from modules import process as k8s
from modules.get_deploy import K8sDeploy

class Images:
    global _logger, k8s_object
    _logger = logger.get_logger('Images')
    k8s_object = 'images'
 
    def __init__(self,ns):
        global k8s_object_list
        self.ns = ns
        if not ns:
            ns = 'all'
        k8s_object_list = K8sDeploy.get_deployments(ns)

    def get_images(v, ns, l):
        data = []
        for item in k8s_object_list.items:
            for container in item.spec.template.spec.containers:
                data.append([item.metadata.namespace, item.metadata.name, container.name, container.image, \
                container.image_pull_policy])
        return data
    
    def list_images(v, ns, l):
        headers = ['NAMESPACE', 'DEPLOYMENT', 'CONTAINER_NAME', 'IMAGE:TAG', \
        'IMAGE_PULL_POLICY']   
        data = Images.get_images(v, ns, l)
        k8s.Output.print_table(data, headers, True, l)

    def get_last_updated_tag(v, ns, l):
        repo = []
        data = Images.get_images(v, ns, l)
        headers = ['NAMESPACE', 'DEPLOYMENT', 'CONTAINER_NAME', 'IMAGE_PULL_POLICY', \
        'IMAGE:TAG', 'LATEST_TAG_AVAILABLE']
        print ("\n[INFO] Checking for latest image tags...")
        result = []
        for image in data:
            image_repo_name = image[3].rsplit(':', 1)[0]
            if not any(x in image_repo_name for x in ['gcr','quay','docker.io']):
                repo_image_url = "https://hub.docker.com/v2/repositories/{}/tags".format(image_repo_name)
                try:
                    results = requests.get(repo_image_url).json()['results']
                except:
                    pass
                
                for repo in results:
                    if not any(x in repo for x in ['dev','latest','beta','rc']):
                        repo_name = repo['name'].rsplit('-', 1)[0]
                        break
            # not feasible for google docker registry as oauth token is needed
            # elif 'gcr' in image_repo_name:
            #     repo_image_url = "https://gcr.io/v2/{}/tags/list".format(image_repo_name)
            #     results = requests.get(repo_image_url).json()
            #     print (results)
            else:
                repo_name = u'\u2717'
            result.append([image[0], image[1], image[2], image[4], image[3], repo_name])
        k8s.Output.print_table(result, headers, True, l)

    def image_recommendation(v, ns, l):
        config_not_defined, if_not_present, always = [], [], []
        headers = ['NAMESPACE', 'DEPLOYMENT', 'CONTAINER_NAME', 'IMAGE:TAG', \
        'IMAGE_PULL_POLICY']
        data = Images.get_images(v, ns, l)
        for image in data:
            if not 'Always' in image[-1]:
                config_not_defined.append(image[3])
            if 'IfNotPresent' in image[-1]:
                if_not_present.append(True)
            if 'Always' in image[-1]:
                always.append(True)
        print ("\n{}: {}".format('images', len(k8s_object_list.items)))
        data_if_not_present = k8s.Output.bar(if_not_present, data,'with image pull-policy', \
        'deployments', '"IfNotPresent"', k8s.Output.YELLOW)
        data_always = k8s.Output.bar(always, data,'with image pull-policy', 'deployments',\
         '"Always"', k8s.Output.GREEN)                
        data_never = k8s.Output.bar(config_not_defined, data, \
        'has not defined recommended image pull-policy', \
        'deployments', '"Always"', k8s.Output.RED)

        if l:
            # creating analysis data for logging
            analysis = {"container_property": "image_pull_policy",
                        "total_images_count": len(data),
                        "if_not_present_pull_policy_containers_count": data_if_not_present,
                        "always_pull_policy_containers_count": data_always,
                        "never_pull_policy_containers_count": data_never}         
            json_data = k8s.Output.json_out(data, analysis, headers, k8s_object, 'image_pull_policy', ns)
            _logger.info(json_data)        

def call_all(v, ns, l):
    Images(ns)
    Images.list_images(v, ns, l)
    Images.image_recommendation(v, ns, l)
    if v: Images.get_last_updated_tag(v, ns, l)

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