from kubernetes import client, config
from kubernetes.client.rest import ApiException

config.load_kube_config()
batch = client.BatchV1Api()

class K8sJobs:
    def get_jobs(ns):
        try:
            print ("\n[INFO] Fetching jobs data...")
            if ns != 'all': 
                namespace = ns
                jobs = batch.list_namespaced_job(namespace, timeout_seconds=10)
            else:             
                jobs = batch.list_job_for_all_namespaces(timeout_seconds=10)
            return jobs
        except ApiException as e:
            print("Exception when calling BatchV1Api->list jobs: %s\n" % e)