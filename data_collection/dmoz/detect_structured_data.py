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
import microdata

#RECIPE = re.compile(r"<[^<]+?((itemtype\s*?=\s*?(\"|\')http://schema\.org/Recipe(\"|\'))|(vocab\s*?=\s*?(\"|\')http://schema\.org/?(\"|\')\s*?typeof\s*?=\s*?(\"|\')Recipe(\"|\')))", re.IGNORECASE)
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
    Note:
        HTML -> {Objects}
        Object -> {Items}
        Item -> {Itemtype, {ItemProperties]}
    '''
    allPages = 0
    objPages = 0
    obj = 0
    for f in filenames:
        infile = indir + "/" + f
        outfile = outdir + "/" + f
        out = open(outfile, "w")
        with open(infile) as lines:
            for line in lines:
                try:
                    allPages += 1
                    data = json.loads(line)
                    html = data['text']
                    data['microdata'] = []
                    data['topic'] = []
                    cont = True
                    while (cont):
                        match = pattern.search(html) #SCHEMA.ORG pattern
                        if allPages%2000 == 0:
                            print f + "\t#Object:" + str(obj) + ":#PageHasObject:" + str(objPages) + ":#Pages:" +  str(allPages)
                        if match:
                            #print match.group(4) #topic
                            #Extract the structured data part
                            #Extract the structured data text
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
                            html = html[search_start:]
                            if len(html) < 10:
                                cont = False
                            try:
                                items = microdata.get_items(structured_data) 
                                #Ref: https://github.com/edsu/microdata
                                for item in items: 
                                    itemtype = item.itemtype
                                    if itemtype:
                                        topic = str(itemtype[0]).split("/")[-1]
                                        data['topic'].append(topic)
                                        data['microdata'].append(item.json_dict())
                                        obj += 1
                                    else:
                                        continue
                            except:
                                traceback.print_exc()
                                continue
                        else:
                            cont = False
                    if len(data['microdata']) > 0:
                        objPages += 1
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

    print "[Filename]:[Number of objects]:[Number of pages that contain object]:[Number of scanned pages]"
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
