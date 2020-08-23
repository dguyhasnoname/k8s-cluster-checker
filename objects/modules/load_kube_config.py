from kubernetes import config

class kubeConfig:
    def load_kube_config():
        try:
            config.load_kube_config()
        except:
            config.load_incluster_config()