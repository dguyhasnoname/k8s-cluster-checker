import sys, time, os, getopt, argparse
start_time = time.time()
from modules.main import GetOpts
from modules import process as k8s
from modules.logging import Logger
from modules.get_ingress import K8sIngress
from modules.get_ns import K8sNameSpace

class _Ingress:
    def __init__(self, namespace, logger):
        self.namespace = namespace
        self.logger = logger
        if not self.namespace:
            self.namespace = 'all'
        self.k8s_object_list = K8sIngress.get_ingress(self.namespace, self.logger) 
        try:
            len(self.k8s_object_list)
        except:
            logger.warning("No ingress found!")
            sys.exit()
        self.k8s_object = 'ingress'

    def ingress_count(self, v, l):
        data, total_ing = [], 0
        ns_list = K8sNameSpace.get_ns(self.logger)
        headers = ['NAMESPACE', 'INGRESS']
        for ns in ns_list.items:
            ing_count = 0
            for item in self.k8s_object_list.items:
                
                if item.metadata.namespace == ns.metadata.name:
                    ing_count += 1
            if ing_count: data.append([ns.metadata.name, ing_count])
        for i in data:
            total_ing = total_ing + i[1]
        data = k8s.Output.append_hyphen(data, '-------')
        data.append(["Total: " , total_ing])
        k8s.Output.print_table(data, headers, True, l)

    def list_ingress(self, v, l):
        headers = ['NAMESPACE', 'INGRESS', 'RULES', 'HOST [SERVICE:PORT]']
        k8s.IngCheck.list_ingress(self.k8s_object_list, self.k8s_object, \
        headers, v, self.namespace, l, self.logger)

def call_all(v, namespace, l, logger):
    call = _Ingress(namespace, logger)
    call.ingress_count(v, l)
    call.list_ingress(v, l)

def main():
    options = GetOpts.get_opts()
    logger = Logger.get_logger(options[4], options[5])
    if options[0]:
        usage()
    if options:
        call_all(options[1], options[2], options[3], logger)
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