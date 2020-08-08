import modules.message
import sys, time, os, getopt, argparse, re, itertools
start_time = time.time()
from modules import process as k8s
from modules.get_crds import K8sCRDs

class _CRDs:
    global k8s_object_list, k8s_object
    k8s_object_list = K8sCRDs.get_crds()
    k8s_object = 'crds'
    #print (k8s_object_list)

    def get_crds(v):
        data, crd_group, count_crd_group_crds, headers = \
        [], [], [], ['CRD_GROUP', 'CRD_COUNT']
        for item in k8s_object_list.items:
            data.append([item.spec.group, item.metadata.name, item.spec.scope])
            crd_group.append([item.spec.group])

        data.sort()
        crd_group.sort()
        # de-duplicate crd groups
        crd_group = list(k for k, _ in itertools.groupby(crd_group))

        # calculate count of crds per crd-group
        for i in crd_group:
            count_crd_group_crds = 0
            for j in data:
                if j[0] == i[0]:
                    count_crd_group_crds += 1
            i.append(count_crd_group_crds)

        crd_group.append(['-----------', '----'])
        crd_group.append(['Total: ' + str(len(crd_group) - 1), len(data)])

        k8s.Output.print_table(crd_group, headers, True)
        k8s.CRDs.check_ns_crd(k8s_object_list, k8s_object, data, headers, v)

        return data

def call_all(v,ns):
    _CRDs.get_crds(v)

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