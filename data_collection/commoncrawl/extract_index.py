import sys
import os
import json
import traceback
from multiprocessing import Pool, cpu_count
from HTMLParser import HTMLParser
from htmlextract import HTMLExtract
unescape = HTMLParser().unescape
from langdetect import detect

def normalize_str(s):
    try:
        return s.strip().lower()
    except:
        return None

def is_filter(s):
    if len(s) == 0:
        return True
    else:
        return False

def extract_text_from_html(html):
    #Return list of normalized sentences 
    #Return None if unsuccessful
    results = []
    e = HTMLExtract()
    try:
        html = unescape(html)
        e.parse(html)
        sentences = e.extract(set(['p', 'li', 'span', 'div', 'h1', 'h2', 'h3', 'h4', 'td', 'small', 'em', 'strong', 'b', 'i']), set(['script', 'style', 'noscript']))
        for s in sentences:
            s = normalize_str(s)
            if not is_filter(s):
                results.append(s)
    except:
        traceback.print_exc()
        return None
    return results


def array2dict(a):
    #return mapping between item in a to its index
    m = {}
    for i in range(len(a)):
        m[a[i]] = i
    return m

def isEnglish(sentences):
    s = ' '.join(sentences)
    if detect(s) != "en":
        return True
    else:
        return False

def process(args):
    results = []
    infile, prop_names = args
    with open(infile) as lines:
        for line in lines:
            data = {}#result
            obj = json.loads(line)
            url = obj['url']
            html = obj['html']
            data['url'] = url
            sentences = extract_text_from_html(html)
            if isEnglish(sentences):
                continue
            if sentences == None:
                continue
            data['text'] = sentences
            dict_sentences = array2dict(sentences) #for finding positive of a given string in sentences faster

            if 'microdata' in obj:
                #Extract positive values
                data['microdata'] = {} #Contains positive values
                for microdata in obj['microdata']:
                    for name in microdata['properties'].keys():
                        if name in prop_names:
                            values = microdata['properties'][name]
                            for item in values:
                                #TODO: item can be dict
                                #item = str(item.encode('utf-8'))
                                if type(item) is unicode:
                                    split_items = item.split("\n") #TODO: Temporary bug
                                    for split_item in split_items:
                                        norm_item = normalize_str(split_item)                                    
                                        if norm_item == None:
                                            continue
                                        if norm_item in dict_sentences:
                                            idx = dict_sentences[norm_item]
                                            if name in data['microdata']:
                                                data['microdata'][name].append(idx)
                                            else:
                                                data['microdata'][name] = [idx]
                                        #else: #examine which item is not in sentences
                                            #print name + "---" + norm_item
                                            #print url
           
                #Extract negative values 
                data['negative'] = {}
                for name in data['microdata']:
                    if len(data['microdata'][name]) > 0:
                        indices = set(data['microdata'][name])
                        data['negative'][name] = [i for i in range(len(sentences)) if i not in indices]
                    else:
                        data['negative'][name] = [i for i in range(len(sentences))]
                print data['microdata']
            results.append(data)
    return results

def read_prop_names(prop_names_file):
    names = []
    with open(prop_names_file) as lines:
        for line in lines:
            names.append(line.strip())
    return names

def extract(args):
    indir = args[0]
    prop_names_file = args[1]
    outfile = args[2]
    out = open(outfile, "w")

    files = os.listdir(indir)
    prop_names = read_prop_names(prop_names_file)
    paras = []
    for f in files:
        fname = indir + "/" + f
        paras.append([fname, prop_names])
    p = Pool(60)
    results = p.map(process, paras)
    for result in results:
        for data in result:
            out.write(json.dumps(data) + "\n")
    out.close()

if __name__=="__main__":
    extract(sys.argv[1:])
