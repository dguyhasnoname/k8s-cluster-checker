import sys, time, os, getopt, argparse
from modules import process as k8s
from modules.get_ingress import K8sIngress
from modules.get_ns import K8sNameSpace

start_time = time.time()

class _Ingress:
    def __init__(self,ns):
        global k8s_object_list, namespace
        self.ns = ns
        if not ns:
            ns = 'all' 
        namespace = ns
        k8s_object_list = K8sIngress.get_ingress(ns)
        if not k8s_object_list: 
            print(k8s.Output.RED + "[ERROR] " + k8s.Output.RESET + "No ingress found!")
            sys.exit()
 
    global k8s_object
    k8s_object = 'ingress'

    def ingress_count():
        data, total_ing = [], 0
        ns_list = K8sNameSpace.get_ns()
        headers = ['NAMESPACE', 'INGRESS']
        for ns in ns_list.items:
            ing_count = 0
            for item in k8s_object_list.items:
                
                if item.metadata.namespace == ns.metadata.name:
                    ing_count += 1
            if ing_count: data.append([ns.metadata.name, ing_count])
        for i in data:
            total_ing = total_ing + i[1]
        data.append(['----------', '---'])
        data.append(["Total: " , total_ing])
        k8s.Output.print_table(data,headers,True)

    def list_ingress(v):
        data = []
        headers = ['NAMESPACE', 'INGRESS', 'RULES', 'HOST [SERVICE:PORT]']
        k8s.IngCheck.list_ingress(k8s_object_list, k8s_object, headers, v, namespace)

def call_all(v,ns):
    _Ingress(ns)
    _Ingress.ingress_count()
    _Ingress.list_ingress(v)

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvn:", ["help", "verbose", "namespace"])
        if not opts:        
            call_all("","")
            k8s.Output.time_taken(start_time)
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
        print(k8s.Output.RED + "[ERROR] " + k8s.Output.RESET + 'Interrupted from keyboard!')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)