import getopt, sys

class GetOpts:
    def get_opts():
        u, verbose, ns, l, format = [''] * 5
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hvn:lf:", ["help", "verbose", \
            "namespace", "logging", 'format'])
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
                l = True                                   
            else:
                assert False, "unhandled option" 

        options = [u, verbose, ns, l, format]
        return options 