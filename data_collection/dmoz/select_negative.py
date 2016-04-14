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

RECIPE = re.compile(r'(http://schema\.org/Recipe)|(\"http://schema.org/\" typeof=\"Recipe\")', re.IGNORECASE)

def select_negative(filenames, indir, outdir, pattern, pos_sites):
    print len(pos_sites)
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
                    print site
                except:
                    traceback.print_exc()
                    print "Error processing " + url 
        out.close()

def main(argv):
    if len(argv) == 0:
        print '[candidate dir] [positive dir] [output dir]'
        return
    indir = argv[0] #Directory that contains candidate
    posdir = argv[1] #Directory that contains positive examples 
    outdir = argv[2] #Output
    if not os.path.exists(outdir): 
        os.makedirs(outdir)

    pos_urls = ExportURL.load_urls(posdir)
    pos_sites = set([])
    for url in pos_urls:
        site = URLUtility.get_host(url)   
        pos_sites.add(site)
    
    print len(pos_sites)
    # return

    #Default
    pattern = RECIPE
    PROCESS_NUMBER = cpu_count()
    if len(argv) == 4:
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
