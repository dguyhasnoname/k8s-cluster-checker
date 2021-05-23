from columnar import columnar
from click import style
from packaging import version
import os, re, time, requests, json, csv

class Output:
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    CYAN = '\033[36m'
    RESET = '\033[0m'
    BOLD = '\033[1;30m'
    # u'\u2717' means values is None or not defined
    # u'\u2714' means value is defined

    global patterns
    patterns = [(u'\u2714', lambda text: style(text, fg='green')), \
                ('True', lambda text: style(text, fg='green')), \
                ('False', lambda text: style(text, fg='yellow'))]

    def time_taken(start_time):
        print(Output.GREEN + "\nTotal time taken: " + Output.RESET + \
        "{}s".format(round((time.time() - start_time), 2)))

    # prints separator line between output
    def separator(color, char, l):
        if l: return
        columns, rows = os.get_terminal_size(0)
        for i in range(columns):
            print (color + char, end="" + Output.RESET)
        print ("\n")      

    # function to append hyphen to print total of any object
    def append_hyphen(data, hyphen):
        temp_bar = []
        [temp_bar.append(hyphen) for x in range(len(data[0]))]
        data.append(temp_bar)

        return data

    # remove unicode characters for reporting
    def remove_unicode(x):
        a = ['No' if v in [u'\u2717', None] else v for v in x]
        b = ['Yes' if v in [u'\u2714'] else v for v in a]
        return b

    # define filename for csv_out and json_out functions
    def filename(directory, ns, k8s_object, config, extension):
        if 'all' in ns:
            filename =  directory + "all_ns_" + k8s_object + "_" + \
            config + "_" + extension
        else:
            filename =  directory + ns + "_"+ k8s_object + "_" + \
            config + "_" + extension
        return filename
 
    # converts list data to csv
    def csv_out(data, headers, k8s_object, config, ns):
        directory = './reports/csv/'
        if not os.path.exists(directory):
            os.makedirs(directory)
        filename = Output.filename(directory, ns, k8s_object, config, 'report.csv')
        with open(filename, "w", newline="") as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(i for i in headers)
            for j in data:
                x = Output.remove_unicode(j)
                writer.writerow(x)
            file.close()

    # generating json data
    def json_out(data, analysis, headers, k8s_object, config, ns):
        json_data = []
        headers = [x.lower() for x in headers]
        for item in data:
            temp_dic = {}
            # storing json data in dict for each list in data
            for i in range(len(headers)):
                for j in range(len(item)):
                    temp_dic.update({headers[i]:item[i]})

            # appending all json dicts to form a list
            json_data.append(temp_dic)
        directory = './reports/json/'
        if not os.path.exists(directory):
            os.makedirs(directory)
        # writing out json data in file based on object type and config being checked
        filename = Output.filename(directory, ns, k8s_object, config, 'report.json')
        f = open(filename, 'w')
        if analysis:
            json_data = {"object": k8s_object,
                        "analysis": analysis,
                        "data": json_data}
        else:
            json_data = {"object": k8s_object,
                        "data": json_data}

        f.write(json.dumps(json_data))
        f.close()

        return json.dumps(json_data)

    # prints table from lists of lists: data
    def print_table(data, headers, verbose, l):
        if verbose and len(data) != 0 and not l:
            table = columnar(data, headers, no_borders=True, \
            patterns=patterns, row_sep='-')
            print (table)
        else:
            return

    # prints analysis in bar format with %age, count and message
    def bar(not_defined, data, message, k8s_object, color, l, logger):
        show_bar = []
        if len(not_defined) == 0:
            return
        percentage = round(((100.0 * len(not_defined) / len(data))), 2)

        for i in range(25):
            if int(i) < percentage / 4:
                show_bar.append(u'\u2588')
            else:
                show_bar.append(u'\u2591')

        if not l:
            if percentage != 0:
                print (color + "{}".format("".join(show_bar)) + Output.RESET + \
                " {}% | {} {} {}.".format(percentage, \
                len(not_defined), message, k8s_object))
            else:
                print (Output.GREEN + "[OK] All {} have config defined."\
                .format(k8s_object) + Output.RESET)
        data = {"count": len(not_defined),
                "percent": percentage}
        return data
