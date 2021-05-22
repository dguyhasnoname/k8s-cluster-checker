import sys, time, os, getopt, argparse, re, itertools
start_time = time.time()
from modules.main import GetOpts
from modules import process as k8s
from modules.get_crds import K8sCRDs

class _CRDs:
    global k8s_object_list, k8s_object
    k8s_object_list = K8sCRDs.get_crds()
    k8s_object = 'crds'
    #print (k8s_object_list)

    def get_crds(v, ns, l):
        data, crd_group, count_crd_group_crds, headers = \
        [], [], [], ['CRD_GROUP', 'CRD_COUNT', 'SCOPE']
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

        crd_group = k8s.Output.append_hyphen(crd_group, '---------')
        crd_group.append(['Total: ' + str(len(crd_group) - 1), len(data)])

        k8s.Output.print_table(crd_group, headers, True, l)

        k8s.CRDs.check_ns_crd(k8s_object_list, k8s_object, data, \
        headers, v, 'all', l)

        return data

def call_all(v, ns, l):
    _CRDs.get_crds(v, ns, l)

def main():
    options = GetOpts.get_opts()
    if options[0]:
        usage()
    if options:
        call_all(options[1], options[2], options[3])
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