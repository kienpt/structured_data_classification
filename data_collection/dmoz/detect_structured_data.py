'''
    Detect pages that contains structured data (schema.org)
    And write these pages to other files

    Usage:
    [input directory of html content] [output directory]
'''

import re
import os
import json
import sys
from multiprocessing import Process

RECIPE = re.compile("(itemtype {0,2}= {0,2}\"http://schema\.org/Recipe\")|(vocab {0,2}= {0,2}\"http://schema\.org/\" {0,2}typeof {0,2}= {0,2}\"Recipe\")")

def find_pattern_pages(filenames, indir, outdir, pattern):
    '''
    Separate all pages that match pattern
    Args:
        - filenames: a list of filenames as input, each file has json line format
        - indir: directory that contains filenames
        - pattern: regex pattern of the target object
        - outdir: output directory
    '''
    total = 0
    hit = 0
    for f in filenames:
        infile = indir + "/" + f
        outfile = outdir + "/" + f
        out = open(outfile, "w")
        with open(infile) as lines:
            for line in lines:
                try:
                    total += 1
                    data = json.loads(line)
                    html = data['text']
                    match = pattern.search(html)
                    if total%5000 == 0:
                        print f + ":" + str(hit) + ":" +  str(total)
                    if match:
                        hit += 1
                        out.write(line)
                except:
                    print "Failed to read a line"
                    continue
                    
        out.close()

def main(argv):
    indir = argv[0]
    outdir = argv[1]
    if not os.path.exists(outdir): 
        os.makedirs(outdir)

    #Default
    PROCESS_NUMBER = 8
    pattern = RECIPE

    if len(argv) == 3:
        PROCESS_NUMBER = int(argv[3])
    jobs = []
    files = os.listdir(indir)
    queues = []

    print "[Filename]:[#Hit pages]:[#Total pages]"
    #Assign files to each process
    for i in range(PROCESS_NUMBER):
        q = []
        for j in range(i, len(files), PROCESS_NUMBER):
            q.append(files[j])
        queues.append(q)
    for q in queues:
        p = Process(target=find_pattern_pages, args=(q, indir, outdir, pattern))
        jobs.append(p)
        p.start()
    for p in jobs:
        p.join()
        
if __name__=="__main__":
   main(sys.argv[1:]) 
