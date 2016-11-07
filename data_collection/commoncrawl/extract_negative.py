from htmlextract import HTMLExtract
import sys
import json
import traceback
import os
from HTMLParser import HTMLParser
from multiprocessing import Pool, cpu_count
unescape = HTMLParser().unescape


def normalize_str(s):
    return s.strip().lower()

def is_filter(s):
    if len(s) == 0:
        return True
    else:
        return False

def read_prop_file(prop_file):
    print "Reading " + prop_file
    url2prop = {}
    with open(prop_file) as lines:
        for line in lines:
            try:
                obj = json.loads(line)
                url = obj['url']
                value = obj['text']
                if url in url2prop:
                    value = normalize_str(value)
                    url2prop[url].add(value)
                else:
                    url2prop[url] = set([value])
            except:
                print "Failed: " + line

    print "Done Reading " + prop_file
    return url2prop

def read_prop_names(prop_names_file):
    names = []
    with open(prop_names_file) as lines:
        for line in lines:
            names.append(line.strip())
    return names

def extract_negative(args):
    '''
    return list of negative fragmented text
    '''

    filename, url2prop, urls = args
    results = []
    e = HTMLExtract()
    with open(filename) as lines:
        for line in lines:
            try:
                obj = json.loads(line)
                url = obj['url']
                if url not in urls:
                    continue
                positives = url2prop[url]
                html = obj['html']
                html = unescape(html)
                e.parse(html)
                sentences = e.extract(['p', 'li', 'span', 'div', 'h1', 'h2', 'h3', 'h4', 'td'],
                ['script', 'style', 'noscript'])
                for s in sentences:
                    s = normalize_str(s)
                    if not is_filter(s):
                        if s not in positives:
                            results.append({'url':url, 'text':s})
            except:
                traceback.print_exc()
                print filename 
                continue
    #sys.stdout.write(str(len(results)) + ",")
    return results



def extract_negative_multiproc(args):
    if len(args) != 4:
        print "[prop_names_file] [html_dir] [prop_dir] [outdir]"
        return
    prop_names_file = args[0]
    html_dir = args[1]
    prop_dir = args[2]
    outdir = args[3]

    prop_names = read_prop_names(prop_names_file)
    
    for name in prop_names: 
        uniq_values = set([]) #make sure that all negative values are not duplicated
        prop_file = prop_dir + "/" + name + ".json"
        url2prop = read_prop_file(prop_file)

        args = []
        htmlfiles = os.listdir(html_dir)
        urls = set(url2prop.keys())
        for f in htmlfiles:
            filename = html_dir + "/" + f
            args.append([filename, url2prop, urls])
        out = open(outdir + "/" + name + "_negatives.json", "w")
        p = Pool(32)
        results = p.map(extract_negative, args)
        for result in results:
            for item in result:
                if item['text'] not in uniq_values:
                    out.write(json.dumps(item) + "\n")
                    uniq_values.add(item['text'])
        out.close()

if __name__=="__main__":
    extract_negative_multiproc(sys.argv[1:])
