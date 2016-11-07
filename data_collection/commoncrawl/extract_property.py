import sys
import os
import traceback
import re
import json
import microdata
from multiprocessing import Pool, cpu_count

#RECIPE_PATTERN = re.compile(r"<[^<]+?((itemtype\s*?=\s*?(\"|\')http://schema\.org/Recipe(\"|\'))|(vocab\s*?=\s*?(\"|\')http://schema\.org/?(\"|\')\s*?typeof\s*?=\s*?(\"|\')Recipe(\"|\')))", re.IGNORECASE)

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
           
def extract_byfile(args):
    '''
    output schema: url, html, microdata, microdata_html
    '''
    infile, outfile, PATTERN = args 
    out = open(outfile, "w")
    with open(infile) as lines:
        for line in lines:
            try:
                data = json.loads(line)
                html = data['html']
                data['microdata'] = []
                cont = True
                while (cont):
                    match = PATTERN.search(html) #SCHEMA.ORG pattern
                    if match:
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
                                    data['microdata'].append(item.json_dict())
                                else:
                                    continue
                        except:
                            traceback.print_exc()
                            continue
                    else:
                        cont = False
                if len(data['microdata']) > 0:
                    out.write(json.dumps(data) + '\n')
            except:
                traceback.print_exc()
                print "EXCEPTION FILE: " + infile 
    out.close()

def extract(indir, outdir, PATTERN):
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    files = os.listdir(indir)
    args = []
    for f in files:
        infile = indir + "/" + f
        outfile = outdir + "/" + f
        if infile.split(".")[-1] != "json":
            continue
        args.append([infile, outfile, PATTERN])
    p = Pool(cpu_count()-2)
    p.map(extract_byfile, args)

def main(argv):
    indir = argv[0]
    outdir = argv[1]
    topic = argv[2]
    TYPES = ['person','product','event','movie','restaurant','recipe','book','tvseries','softwareapplication','jobposting','drug']
    if topic not in TYPES:
        print "Check again your topic, it might be wrong"
        print TYPES
        return
    PATTERN = generate_pattern([topic])
    extract(indir, outdir, PATTERN)
    
if __name__=="__main__":
    print "Arguments: [indir] [outdir] [topic]"
    main(sys.argv[1:])
