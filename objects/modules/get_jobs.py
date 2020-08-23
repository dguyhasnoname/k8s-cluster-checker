from kubernetes import client
from kubernetes.client.rest import ApiException
from .load_kube_config import kubeConfig

kubeConfig.load_kube_config()
batch = client.BatchV1Api()

class K8sJobs:
    def get_jobs(ns):
        try:
            if ns != 'all':
                print ("\n[INFO] Fetching {} namespace jobs data...".format(ns))  
                namespace = ns
                jobs = batch.list_namespaced_job(namespace, timeout_seconds=10)
            else:
                print ("\n[INFO] Fetching all namespace jobs data...")   
                jobs = batch.list_job_for_all_namespaces(timeout_seconds=10)
            return jobs
        except ApiException as e:
            print("Exception when calling BatchV1Api->list jobs: %s\n" % e)