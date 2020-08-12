# k8s-cluster-checker

![Docker Pulls](https://img.shields.io/docker/pulls/dguyhasnoname/k8s-cluster-checker.svg)
[![docker image version](https://images.microbadger.com/badges/version/dguyhasnoname/k8s-cluster-checker.svg)](https://microbadger.com/images/dguyhasnoname/k8s-cluster-checker)
[![PyPI version](https://badge.fury.io/py/kubernetes.svg)](https://badge.fury.io/py/kubernetes)


![logo](/docs/imgs/logo.png)

k8s-cluster-checker is bundle of python scripts which can be used to analyse below configurations in a kubernetes cluster:

- OS version(supports flatcar OS and coreOS only)
- Kubernetes version
- Docker version
- Admission Controllers
- security-context of workloads
- health-probes of workloads
- QoS of workloads
- types of services
- workload running with single replica
- rbac analysis
- k8s objects in a namespace 
- stale namespaces with no workloads
 
Once the tool is run, it generates output in 3 ways:
1. stdout on the screen to visualise the analysis right away.
2. report in `csv` files are generated for each analysis. A combined report is generated in excel file. You can use it for your own custom analysis.
3. json output is generated for each analysis which can be consumed in down-stream scripts.

#### Compatible k8s versions: 1.14+  
Running k8s-cluster-check on older k8s version 1.10.x to 1.13.x may result in missing results/exceptions. Tool do not support k8s version previous to 1.10.x.

This tool performs read-only operations on any k8s cluster. You can make a service account/kubeconfig with full read-only access to all k8s-objects and use the same to run the tool.

#### k8s-cluster-checker contains below scripts:

1. [cluster.py](objects/cluster.py): gives quick details of cluster and analyses configurations as below:
    - cluster name
    - node-details
    - node-roles
    - volumes used
    - OS, K8s and docker version. Also checks for latest versions.
    - overall and namespaced workload count
    - analysis of admision-controllers
    - analysis of security configs for workloads
    - analysis of health-check probes
    - analysis of resource limits/requests of workloads and their QoS
    - analysis of image-pull-policy
    - RBAC analysis
    - analysis of services in the cluster.

    above analysis is the collective result of following scripts.
2. [nodes.py](objects/nodes.py): gives details of nodes. Finds if docker, kubernetes and docker version are latest or not.
3. [namespace.py](objects/namespace.py): give details of namespace objects and analyses them
    - `python namespace.py -n kube-system -v`
    - if `-n` namespace is not given, it will return data for all namespaces
    - `-v` gives more details, this flag is valid for all scripts
4. [control_plane.py](objects/control_plane.py): analyses control-plane configuration and reports missing ones
5. [deployments.py](objects/deployments.py): gives detail for deployments in cluster and analyses them
6. [daemonsets.py](objects/daemonsets.py): gives detail for daemonsets in cluster and analyses them
7. [statefulsets.py](objects/statefulsets.py): gives detail for statefulsets in cluster and analyses them
8. [services.py](objects/services.py): gives detail for services in cluster and analyses them
9. [jobs.py](objects/jobs.py): gives detail for jobs in cluster and analyses them
10. [pods.py](objects/pods.py): gives detail for pods in cluster in all namespaces and analyses them
11. [ingress.py](objects/ingress.py): gives detail for ingress in cluster and analyses them
12. [rbac.py](objects/rbac.py): gives detail for rbac in cluster and analyses them
13. [images.py](objects/images.py): gives detail for images used by workloads in cluster and reports back if any old images found.

## Pre-requisites

1. python3 with below [packages](requirements.txt):
    - pandas
    - kubernetes
    - argparse
    - columnar
    - click
    - requests
    - futures
    - packaging
    - xlsxwriter

2. `pip3` needs to be installed to get above packages. `pip` is already installed if you are using Python 2 >=2.7.9 or Python 3 >=3.4. You need to install above packages with command: 

    ```
    pip3 install <package-name>
    ```

    A docker image is available on [dockerhub](https://hub.docker.com/repository/docker/dguyhasnoname/k8s-cluster-checker) with all the dependencies installed. Follow this readme for docker image instructions.

3. KUBECONFIG for the cluster needs to be exported as env. It is read by k8s-cluster-checker scripts to connect to the cluster.

## How to run k8s-cluster-checker scripts

Once above pre-requisites are installed and configred, you are ready to run k8s-cluster-checker scripts as below:

1. Change dir: `cd objects`
2. Run scripts:

    ```
    python cluster.py
    ```

If you want a ready-made env to run k8s-cluster-checker, please build the docker image using below command:

    docker build -t <image_name>:<tag_name> .

e.g.

    
    docker build -t dguyhasnoname/k8s-cluster-checker:latest .
    
Running through docker image would be much easier than installing dependencies on your machine. The docker image being used is based on `python:3.8-slim-buster` which is a very light weight version of python in docker.  

Please check [dockerhub](https://hub.docker.com/repository/docker/dguyhasnoname/k8s-cluster-checker) for latest image, if you do not want to build your own image. You can download the latest image from dockerhub as the dockerhub image build is integrated with this repo and it polls this repo for update.

    docker pull dguyhasnoname/k8s-cluster-checker:latest

Once your image is ready, run the docker container and export KUBECONFIG inside the container. You can get the kubeconfig inside the container by mapping dir inside the container from your local machine where your KUEBCONFIG file is stored:

    
    docker run -it -v /dguyhasnoname/k8sconfig:/k8sconfig dguyhasnoname/k8s-cluster-checker:latest
    

Now you should be inside the container. Please export KUBECONFIG:

    
    export KUBECONFIG=/k8sconfig/<your_kubeconfig_filename>
    

Now you are ready to run k8s-cluster-checker scripts:

    
    cd /apps
    python cluster.py

### Sample run

![sample_run_1](/docs/imgs/sample_run_1.png)
![sample_run_3](/docs/imgs/sample_run_3.png)
![sample_run](/docs/imgs/sample_run.png)

## Contributions/Issues

If you find any bug, please feel free to open an issue in this repo. If you want to contribute, PRs are welcome.