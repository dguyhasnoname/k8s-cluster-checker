from kubernetes import client, config
from kubernetes.client.rest import ApiException
import sys, time, os, re
import datetime
import requests
import objects as k8s
import deployments as deployments

start_time = time.time()

class Images:
    global k8s_object, k8s_object_list, namespace
    k8s_object_list = deployments.Deployment.get_deployments()

    def get_images():
        data = []
        for item in k8s_object_list.items:
            for container in item.spec.template.spec.containers:
                data.append([item.metadata.name, container.name, container.image, container.image_pull_policy])
        return data
    
    def list_images():
        headers = ['DEPLOYMENT', 'CONTAINER_NAME', 'IMAGE', 'IMAGE_PULL_POLICY']   
        data = Images.get_images()
        k8s.Output.print_table(data,headers)

    def get_last_updated_tag():
        data = Images.get_images()
        headers = ['DEPLOYMENT', 'CONTAINER_NAME', 'IMAGE_PULL_POLICY', 'IMAGE', 'LATEST_TAG_AVAILABLE'] 
        result = []
        for image in data:
            image_repo_name = image[2].rsplit(':', 1)[0]
            if not any(x in image_repo_name for x in ['gcr','quay','docker.io']):
                repo_image_url = "https://hub.docker.com/v2/repositories/{}/tags".format(image_repo_name)
                results = requests.get(repo_image_url).json()['results']
                
                for repo in results:
                    if not any(x in repo for x in ['dev','latest','beta','rc']):
                        repo['name'] = repo['name'].rsplit('-', 1)[0]
                        break
            # not feasible for google docker registry as oauth token is needed
            # elif 'gcr' in image_repo_name:
            #     repo_image_url = "https://gcr.io/v2/{}/tags/list".format(image_repo_name)
            #     results = requests.get(repo_image_url).json()
            #     print (results)
            else:
                repo['name'] = u'\u2717'
            result.append([image[0], image[1], image[3], image[2], repo['name']])
        k8s.Output.print_table(result,headers)
        
                        
        
                    

def main():
    #Images.list_images()
    Images.get_last_updated_tag()
    print(k8s.Output.GREEN + "Total time taken: " + k8s.Output.RESET + "{}s".format(round((time.time() - start_time), 2)))

if __name__ == "__main__":
    main()