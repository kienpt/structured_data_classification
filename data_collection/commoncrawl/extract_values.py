import sys
import os
import json
import traceback
from multiprocessing import Pool, cpu_count
from langdetect import detect

counter = {} 

def extract_values(args):
    #Return 2 arrays: one is ingredent array and one is instruction array #recipe domain
    infile, prop_names = args
    prop2values = {} #key is prop_names and value is a list of prop values
    for name in prop_names:
        prop2values[name] = []
    with open(infile) as lines:
        for line in lines:
            obj = json.loads(line)
            url = obj['url']
            if 'microdata' in obj:
                for microdata in obj['microdata']:
                    for name in microdata['properties'].keys():
                        try:
                            if name in counter:
                                counter[name] += 1
                            else:
                                counter[name] = 1
                            if name in prop2values:
                                values = microdata['properties'][name]
                                #s = ' '.join(values) #joining to reduce time for detecting language
                                #if detect(s) != "en":
                                #   continue
                                for item in values:
                                    prop2values[name].append({'url':url, 'text':item})
                        except:
                            traceback.print_exc()
                            continue
    return prop2values 

def count_properties(infile):
    #Return a map between attribute name and it's counter
    counter = {}
    with open(infile) as lines:
        for line in lines:
            obj = json.loads(line)
            url = obj['url']
            if 'microdata' in obj:
                for microdata in obj['microdata']:
                    for name in microdata['properties'].keys():
                        try:
                            if name in counter:
                                counter[name] += 1
                            else:
                                counter[name] = 1
                        except:
                            traceback.print_exc()
                            continue
    return counter 

def count_properties_multiproc(indir, prop_names):
    files = os.listdir(indir)
    files = [indir + "/" + f for f in files]
    p = Pool(cpu_count()-2)
    results = p.map(count_properties, files)

    #merge counter
    dict_counter = {}
    for counter in results:
        for key in counter:
            if key not in dict_counter:
                dict_counter[key] = counter[key]
            else:
                dict_counter[key] += counter[key]
    
    #flaten counter and sort 
    ar_counter = []

    for key in dict_counter:
        ar_counter.append([key, dict_counter[key]])
    ar_counter.sort(key=lambda x:x[1])
    max_count = ar_counter[-1][1]
    for item in ar_counter:
        if item[1] > max_count/5:
            print item[0] + " " + str(item[1])
              
def extract_values_multiproc(indir, prop_names, outdir):
    files = os.listdir(indir)
    prop2file = {}
    for name in prop_names:
        out = open(outdir + "/" + name + ".json", "w")
        prop2file[name] = out
        
    files = [indir + "/" + f for f in files]
    args = []
    for f in files:
        args.append([f, prop_names])
    p = Pool(cpu_count()-2)
    results = p.map(extract_values, args)
    for result in results:
        for name in result:
            for value in result[name]:
                prop2file[name].write(json.dumps(value) + "\n")
    for name in prop2file:
        prop2file[name].close()

def read_prop_names(prop_names_file):
    names = []
    with open(prop_names_file) as lines:
        for line in lines:
            names.append(line.strip())
    return names

def main(args):
    option = args[0]
    if option == "extract":
        indir = args[1]
        outfile = args[2]
        prop_names_file = args[3]
        prop_names = read_prop_names(prop_names_file)
        outdir = outfile
        extract_values_multiproc(indir, prop_names, outdir)
    if option == "stat":
        indir = args[1]
        outfile = args[2]
        count_properties_multiproc(indir, outfile) 
    
if __name__=="__main__":
    print "extract [indir] [outdir] [prop_names_file]"
    print "stat [indir] [outfile]"
    print "indir: html_property"
    main(sys.argv[1:])
