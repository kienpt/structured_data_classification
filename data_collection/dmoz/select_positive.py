'''
Select positive pages - ones that contains schema.org markup of the target object, from the candidate directory for training
Usage:
    [input directory that contains json data] [output directory]
'''

import sys
import re
import os
import json
from multiprocessing import Process, cpu_count
import traceback

#RECIPE = re.compile(r"<[^<]+?((itemtype\s*?=\s*?(\"|\')http://schema\.org/Recipe(\"|\'))|(vocab\s*?=\s*?(\"|\')http://schema\.org/?(\"|\')\s*?typeof\s*?=\s*?(\"|\')Recipe(\"|\')))", re.IGNORECASE)

def generate_pattern(topics):
    '''
    Return compiled regex pattern to match topic
    '''
    topics_pattern = '('
    for topic in topics:
        topics_pattern += topic + "|"
    topics_pattern = topics_pattern.strip("|") + ")"
    pattern_string = r"<[^<]+?((itemtype\s*?=\s*?(\"|\')http://schema\.org/" + topics_pattern + "(\"|\'))|(vocab\s*?=\s*?(\"|\')http://schema\.org/?(\"|\')\s*?typeof\s*?=\s*?(\"|\')" + topics_pattern + "(\"|\')))"
    pattern = re.compile(pattern_string, re.IGNORECASE)
    return pattern


def select_positive(files, indir, outdir, pattern):
    '''
    Select example that follows the regex patterns
    '''
    for f in files:
        filename = indir + "/" + f
        outfile = outdir + "/" + f
        with open(filename) as lines:
            out = open(outfile, "w")
            for line in lines:
                data = json.loads(line)
                html = data['text']
                url = data['url']

                #Filter one that have more than 2 patterns, since usually it is a list of description, not the object
                matches = pattern.findall(html) 
                if len(matches) > 2:
                    continue
                #Filter one that contains itemListElement. i.e http://www.simplyrecipes.com/recipes/cuisine/italian/
                if (data['itemlist']>0) & (data['itemprop']>0):
                    continue
                out.write(line) 
                 
            out.close()

def main(argv):
    if len(argv) == 0:
        print "Args: [Topic] [Candidate Directory] [Output Directory]"     
        print "[Topic]: Name of a topic or filename that contains list of topics"
        print "[Candidate Directory]: Directory that contains candidate pages"
        print "[Output Directory]: Empty directory - if not existed, it will be created automatically"
        sys.exit(1)

    topic = argv[0]
    indir = argv[1]
    outdir = argv[2]
    if not os.path.exists(outdir): 
        os.makedirs(outdir)
    
    if os.path.isfile(topic):
        topics = map(str.strip, open(topic).readlines())
    else:
        topics = [topic]
    pattern = generate_pattern(topics)

    PROCESS_NUMBER = cpu_count()-2
    if len(argv) == 4:
        PROCESS_NUMBER = int(argv[3])
    jobs = []
    queues = []
    
    files = os.listdir(indir)
    for i in range(PROCESS_NUMBER):
        q = []
        for j in range(i, len(files), PROCESS_NUMBER):
            q.append(files[j])
        queues.append(q)
    for q in queues:
        p = Process(target=select_positive, args=(q, indir, outdir, pattern))
        jobs.append(p)
        p.start()
    for p in jobs:
        p.join()


if __name__=="__main__":
    main(sys.argv[1:])
