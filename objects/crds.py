import sys, time, os, getopt, argparse, re, itertools
start_time = time.time()
from modules.main import ArgParse
from modules import process as k8s
from modules.logging import Logger
from modules.get_crds import K8sCRDs

class _CRDs:
    def __init__(self, logger):
        self.logger = logger
        self.k8s_object = 'crds'
        self.k8s_object_list = K8sCRDs.get_crds(self.logger)

    def get_crds(self, v, ns, l):
        data, crd_group, count_crd_group_crds, headers = \
        [], [], [], ['CRD_GROUP', 'CRD_COUNT', 'SCOPE']
        for item in self.k8s_object_list.items:
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

        k8s.CRDs.check_ns_crd(self.k8s_object_list, self.k8s_object, data, \
        headers, v, 'all', l, self.logger)

        return data

def call_all(v, ns, l, logger):
    call = _CRDs(logger)
    call.get_crds(v, ns, l)

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