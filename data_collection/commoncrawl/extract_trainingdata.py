'''
Separate positive and negative sentences from index data (one that contains sentences and indices of positive and negative sentences)
'''
import sys
import json
import traceback
import os

def read_prop_names(prop_names_file):
    names = []
    with open(prop_names_file) as lines:
        for line in lines:
            names.append(line.strip())
    return names

def extract(args):
    infile = args[0]
    outdir = args[1]
    prop_names_file = args[2]
    prop_names = read_prop_names(prop_names_file)
    pos = {}
    neg = {}
    set_pos = {}
    set_neg = {}
    for name in prop_names:
        positive_file = open(outdir + "/" + name + "_positive.json", "w")
        negative_file = open(outdir + "/" + name + "_negative.json", "w")
        pos[name] = positive_file
        neg[name] = negative_file
        set_pos[name] = set([])
        set_neg[name] = set([])


    with open(infile) as lines:
        for line in lines:
            obj = json.loads(line)
            if ("recipeInstructions" in obj['microdata']) | ("ingredients" in obj['microdata']):
                url = obj['url']
                for name in obj['microdata']:
                    indices = obj['microdata'][name]
                    for idx in indices:
                        text = obj['text'][idx]
                        if text not in set_pos[name]:
                            pos[name].write(json.dumps({'url':url,'text':text}) + "\n")
                            set_pos[name].add(text)
                for name in obj['negative']:
                    indices = obj['negative'][name]
                    for idx in indices:
                        text = obj['text'][idx]
                        if text not in set_neg[name]:
                            neg[name].write(json.dumps({'url':url,'text':text}) + "\n")
                            set_neg[name].add(text)

    for key in pos:
        pos[key].close()
    for key in neg:
        neg[key].close()

if __name__=="__main__":
    print "[infile] [outdir] [prop_names_file]"
    print "infile: index file"
    print "outdir: new directory where the results are stored"
    extract(sys.argv[1:])
