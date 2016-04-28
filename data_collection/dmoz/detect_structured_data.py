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
from multiprocessing import Process, cpu_count
import traceback

#RECIPE = re.compile(r"<[^<]+?((itemtype\s*?=\s*?(\"|\')http://schema\.org/Recipe(\"|\'))|(vocab\s*?=\s*?(\"|\')http://schema\.org/?(\"|\')\s*?typeof\s*?=\s*?(\"|\')Recipe(\"|\')))", re.IGNORECASE)
ITEMPROP = re.compile(r'(itemprop|property)', re.IGNORECASE)
ITEMLIST = re.compile(r'itemListElement', re.IGNORECASE)

def generate_pattern(topics):
    '''
    Return compiled regex pattern to match topic
    '''
    topics_pattern1 = '(?P<topic1>'
    topics_pattern2 = '(?P<topic2>'
    for topic in topics:
        topics_pattern1 += topic + "|"
        topics_pattern2 += topic + "|"
    topics_pattern1 = topics_pattern1.strip("|") + ")"
    topics_pattern2 = topics_pattern2.strip("|") + ")"
    pattern_string = r"<[^<]+?((itemtype\s*?=\s*?(\"|\')http://schema\.org/" + topics_pattern1 + "(\"|\'))|(vocab\s*?=\s*?(\"|\')http://schema\.org/?(\"|\')\s*?typeof\s*?=\s*?(\"|\')" + topics_pattern2 + "(\"|\')))"
    pattern = re.compile(pattern_string, re.IGNORECASE)
    return pattern
    

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
                    match = pattern.search(html) #SCHEMA.ORG pattern
                    if total%5000 == 0:
                        print f + "\tFound:" + str(hit) + ":Processed:" +  str(total)
                    if match:
                        #print match.group(4) #topic
                        #Extract the structured data part
                        start = match.start(0)
                        anchor_text = match.group(0)
                        element_name = anchor_text.split(' ')[0].strip('<').strip()
                        #print element_name
                        element_count = 1
                        element_pattern = re.compile(r'</?'+element_name+r'>?', re.IGNORECASE)
                        search_start = match.end(0)
                        while element_count > 0:
                            element_match = element_pattern.search(html[search_start:])
                            if element_match:
                                #if '/' in element_match.group(0):
                                if element_match.group(0)[1] == '/':#Is this a close tag
                                    element_count -= 1
                                else:
                                    element_count += 1
                                search_start += element_match.end(0)
                            else:
                                #If there is no element_match, that means the close element tag does not exist
                                search_start = len(html)
                                break
                        structured_data = html[start:search_start]
                        item_prop = ITEMPROP.findall(structured_data)
                        item_list = ITEMLIST.findall(structured_data)
                        data['structured'] = structured_data
                        data['itemprop'] = len(item_prop)
                        data['itemlist'] = len(item_list)
                        if match.group('topic1'):
                            data['topic'] = match.group('topic1').lower()
                        else:
                            data['topic'] = match.group('topic2').lower()
                        hit += 1
                        out.write(json.dumps(data) + '\n')
                except:
                    traceback.print_exc()
                    print "Failed to read a line"
                    continue
                    
        out.close()

def main(argv):
    if len(argv) == 0:
        print "Args: [Topic] [Input Directory] [Output Directory]"     
        print "[Topic]: Name of a topic or filename that contains list of topics"
        print "[Input Directory]: Directory that contains html content in JSON format"
        print "[Output Directory]: Empty directory - if not existed, it will be created automatically"
        sys.exit(1)

    topic = argv[0]
    indir = argv[1]
    outdir = argv[2]
    if not os.path.exists(outdir): 
        os.makedirs(outdir)

    #Default
    PROCESS_NUMBER = cpu_count()-2
    if os.path.isfile(topic):
        topics = map(str.strip, open(topic).readlines())
    else:
        topics = [topic]
    pattern = generate_pattern(topics)

    if len(argv) == 4:
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
