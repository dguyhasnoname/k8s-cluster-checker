import time, os, json, sys
start_time = time.time()
from modules.main import ArgParse
from modules.logging import Logger
from modules import process as k8s
from modules.get_svc_acc import K8sSvcAcc

class ServiceAccount:
    def __init__(self, namespace, logger):
        self.namespace = namespace
        self.logger = logger
        if not self.namespace:
            self.namespace = 'all'
        self.k8s_object_list = K8sSvcAcc.get_svc_acc(self.namespace) 
        self.k8s_object = 'serviceaccount'

    def get_namespaced_sa_list(self, v, l):
        data = []
        headers = ['NAMESPACE', 'SERVICE_ACCOUNT', 'SECRET']
        for item in self.k8s_object_list.items:
            for j in item.secrets:
                data.append([item.metadata.namespace, item.metadata.name, j.name])
        if v: print ("Total service accounts: {}".format(len(data)))            
        k8s.Output.print_table(data, headers, True, l)
        return data

def call_all(v, namespace, l, logger):
    call = ServiceAccount(namespace, logger)
    call.get_namespaced_sa_list(v, l)

def main():
    args = ArgParse.arg_parse()
    # args is [u, verbose, ns, l, format, silent]
    logger = Logger.get_logger(args.format, args.silent)
    if args:
        call_all(args.verbose, args.namespace, args.logging, logger)
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