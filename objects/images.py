import sys, time, os, re, getopt
import requests
from modules import process as k8s
from modules.get_deploy import K8sDeploy

start_time = time.time()

class Images:
    def __init__(self,ns):
        global k8s_object_list
        self.ns = ns
        if not ns:
            ns = 'all'
        k8s_object_list = K8sDeploy.get_deployments(ns)

    def get_images():
        data = []
        for item in k8s_object_list.items:
            for container in item.spec.template.spec.containers:
                data.append([item.metadata.namespace, item.metadata.name, container.name, container.image, \
                container.image_pull_policy])
        return data
    
    def list_images():
        headers = ['NAMESPACE', 'DEPLOYMENT', 'CONTAINER_NAME', 'IMAGE:TAG', 'IMAGE_PULL_POLICY']   
        data = Images.get_images()
        k8s.Output.print_table(data,headers)

    def get_last_updated_tag():
        repo = []
        data = Images.get_images()
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
        k8s.Output.print_table(result,headers,True)

    def image_recommendation():
        config_not_defined, if_not_present, always = [], [], []
        data = Images.get_images()
        for image in data:
            if not 'Always' in image[-1]:
                config_not_defined.append(image[3])
            if 'IfNotPresent' in image[-1]:
                if_not_present.append(True)
            if 'Always' in image[-1]:
                always.append(True)
        print ("\n{}: {}".format('images', len(k8s_object_list.items)))
        k8s.Output.bar(if_not_present, data,'with image pull-policy', \
        'deployments', '"IfNotPresent"', k8s.Output.YELLOW)
        k8s.Output.bar(always, data,'with image pull-policy', 'deployments',\
         '"Always"', k8s.Output.GREEN)                
        k8s.Output.bar(config_not_defined, data, 'has not defined recommended image pull-policy', \
        'deployments', '"Always"', k8s.Output.RED)

def call_all(v,ns):
    Images(ns)
    # Images.list_images()
    Images.image_recommendation()
    if v: Images.get_last_updated_tag()

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvn:", ["help", "verbose", "namespace"])
        if not opts:        
            call_all("","")
            sys.exit()
            
    except getopt.GetoptError as err:
        print(err)
        return
    verbose, ns = '', ''
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-v", "--verbose"):
            verbose = True
        elif o in ("-n", "--namespace"):
            if not verbose: verbose = False
            ns = a          
        else:
            assert False, "unhandled option"
    call_all(verbose,ns)
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