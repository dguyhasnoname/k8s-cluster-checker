# k8s-cluster-checker

k8s-cluster-checker is bundle of python scripts which can be used to analyse below configurations in a kubernetes cluster:

1. security-context defined
2. health-probes defined
3. QoS of workloads
4. types of services
5. workload running with single replica
6. rbac details
7. k8s objects in a namespace

## Pre-requisites

1. python3 with below packages:
    - kubernetes
    - argparse
    - columnar
    - click
    - requests
2. `pip3` needs to be installed to get above packages. `pip` is already installed if you are using Python 2 >=2.7.9 or Python 3 >=3.4. You need to install above packages with command: 

    ```
    pip3 install <package-name>
    ```

3. KUBECONFIG for the cluster needs to be exported as env. It is read by k8s-cluster-checker scripts to connect to the cluster.

## How to run k8s-cluster-checker scripts

Once above pre-requisites are installed and configred, you are ready to run k8s-cluster-checker scripts as below:

1. Change dir: `cd objects`
2. Run scripts:

    ```
    python cluster.py
    ```

If you want a ready-made env to run k8s-cluster-checker, please build the docker image using below command:

    ```
    docker build -t <image_name>:<tag_name> .

    ```

e.g.

    ```
    docker build -t dguyhasnoname/k8s-cluster-checker:1.0 .
    ```
Once your image is ready, run the docker container and export KUBECONFIG inside the container. You can get he kubeconfig inside the container by mapping dir inside the container from your local machine where you KUEBCONFIG file is stored:

    ```
    docker run -it -v /dguyhasnoname/k8sconfig:/k8sconfig dguyhasnoname/k8s-cluster-checker:1.0
    ```

Now you should be inside the container. Please export KUBECONFIG:

    ```
    export KUBECONFIG=/k8sconfig/<your_kubeconfig_filename>
    ```

Now you are ready to run k8s-cluster-checker scripts:

    ```
    cd /apps
    ```

    ```
    python cluster.py
    ```

## about k8s-cluster-checker scripts

1. ![cluster.py](objects/cluster.py): gives quick details of cluster and analyses configurations
2. nodes.py: gives details of nodes
3. namespace.py: give details of namespace objects and analyses them
4. control_plane.py: analyses control-plane configuration and reports missing ones
5. deployments.py: gives detail for deployments in cluster and analyses them
6. daemonsets.py: gives detail for daemonsets in cluster and analyses them
7. statefulsets.py: gives detail for statefulsets in cluster and analyses them
8. services.py: gives detail for services in cluster and analyses them
9. jobs.py: gives detail for jobs in cluster and analyses them
10. pods.py: gives detail for pods in cluster in all namespaces and analyses them
11. ingress.py: gives detail for ingress in cluster and analyses them
12. rbac.py: gives detail for rbac in cluster and analyses them
13. images.py: gives detail for images used by workloads in cluster and reports back if any old images found.








