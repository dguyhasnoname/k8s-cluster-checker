import getopt, sys

class GetOpts:
    def get_opts():
        u, verbose, ns, l, format, silent = [''] * 6
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hvn:lf:s", ["help", "verbose", \
            "namespace", "logging", 'format', 'silent'])
        except getopt.GetoptError as err:
            print("[ERROR] {}. ".format(err) + \
            "Please run script with -h flag to see valid options.")
            sys.exit(0)

        for o, a in opts:
            if o in ("-h", "--help"):
                u = True
            elif o in ("-v", "--verbose"):
                verbose = True
            elif o in ("-n", "--namespace"):
                ns = a
            elif o in ("-l", "--logging"):
                l = True
            elif o in ("-f", "--format"):
                format = a
            elif o in ("-s", "--silent"):
                silent = True                                                  
            else:
                assert False, "unhandled option" 

        options = [u, verbose, ns, l, format, silent]
        return options 

import argparse

class ArgParse:
    def arg_parse():
        p = argparse.ArgumentParser(description='k8s-cluster-cheker is a tool to anlayse configurations of a k8s cluster: '
                            ' OS version(supports flatcar OS, coreOS & Ubuntu only)'
                            ', Kubernetes version'
                            ', Docker version'
                            ', Admission Controllers'
                            ', security-context of workloads'
                            ', health-probes of workloads'
                            ', QoS of workloads'
                            ', types of services'
                            ', workload running with single replica'
                            ', rbac analysis'
                            ', stale namespaces with no workloads')
        p.add_argument('-v', '--verbose', action='store_true', help='verbose mode. Use this flag to get namespaced pod level config details.')
        p.add_argument('-n', '--namespace', help='pass kubeconfig of the cluster. If not passed, picks KUBECONFIG from env')
        p.add_argument('-l', '--logging', help='Use this flag to generate logs in json format')
        p.add_argument('-f', '--format', help='Use this flag to generate output in given format. csv|json. Default is table format.')
        p.add_argument('-s', '--silent', help='Use this flag to silence the logging. Get only proccessed output.')
        p.add_argument('-b', '--body', nargs = 1, help="JSON file to be processed", type=argparse.FileType('r'))
        p.add_argument('--loglevel', default='INFO', help='sets logging level. default is INFO')

        args = p.parse_args()
        return args        