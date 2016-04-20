'''
'''

import sys
import re
import os
import json
sys.path.append(os.path.dirname(__file__) + "/common")
sys.path.append("common")
from urlutility import URLUtility 
from exporturls import ExportURL
from multiprocessing import Process, cpu_count
import traceback
import exporturls

#RECIPE = re.compile(r'(http://schema\.org/Recipe)|(\"http://schema.org/\" typeof=\"Recipe\")', re.IGNORECASE)

def generate_pattern(topic):
    pattern_string = r'(http://schema\.org/' + topic + ')|(\"http://schema.org/\" typeof=\"' + topic + '\")'
    pattern = re.compile(pattern_string, re.IGNORECASE)
    return pattern

def select_negative(filenames, indir, outdir, pattern, pos_sites):
    for f in filenames:
        infile = indir + "/" + f
        outfile = outdir + "/" + f
        out = open(outfile, "w")
        with open(infile) as lines:
            for line in lines:
                try:
                    data = json.loads(line)
                    url = data['url'] 
                    html = data['text']
                    site = URLUtility.get_host(url)
                    if site in pos_sites:
                        match = pattern.search(html)
                        if match == None:
                            out.write(line)
                except:
                    traceback.print_exc()
                    print "Error processing " + url 
        out.close()

def main(argv):
    if len(argv) == 0:
        print "Args: [All HTML Directory] [Candidate Directory] [Output Directory]"     
        print "[Topic]: topic from schema.org"
        print "[All HTML Directory]: Directory that contains collected pages in JSON format"
        print "[Candidate Directory]: Directory that contains candidate pages"
        print "[Output Directory]: Empty directory - if not existed, it will be created automatically"
        sys.exit(1)

    topic = argv[0]
    indir = argv[1] #Directory that contains all collected pages 
    posdir = argv[2] #Directory that contains candidate pages
    outdir = argv[3] #Output
    if not os.path.exists(outdir): 
        os.makedirs(outdir)

    pos_urls = ExportURL.load_urls(posdir)
    pos_sites = set([])
    for url in pos_urls:
        site = URLUtility.get_host(url)   
        pos_sites.add(site)
    
    print "Number of candidate sites: " + str(len(pos_sites))

    pattern = generate_pattern(topic)

    PROCESS_NUMBER = cpu_count()-2
    if len(argv) == 5:
        PROCESS_NUMBER = int(argv[4])
    jobs = []
    queues = []
    
    files = os.listdir(indir)
    for i in range(PROCESS_NUMBER):
        q = []
        for j in range(i, len(files), PROCESS_NUMBER):
            q.append(files[j])
        queues.append(q)
    for q in queues:
        p = Process(target=select_negative, args=(q, indir, outdir, pattern, pos_sites))
        jobs.append(p)
        p.start()
    for p in jobs:
        p.join()


if __name__=="__main__":
    main(sys.argv[1:])
