import sys
import os
import json
from multiprocessing import Pool
import traceback
import re
from langdetect import detect

sys.path.append(os.path.dirname(__file__) + "/common")
sys.path.append("common")
from boilerpipe.extract import Extractor
#from bs4 import BeautifulSoup

RECIPE_SCHEMA = re.compile(r"<[^<]+?((itemtype\s*?=\s*?(\"|\')http://schema\.org/Recipe(\"|\'))|(vocab\s*?=\s*?(\"|\')http://schema\.org/?(\"|\')\s*?typeof\s*?=\s*?(\"|\')Recipe(\"|\')))", re.IGNORECASE)
RECIPE = re.compile(r"http://schema\.org/Recipe", re.IGNORECASE)

extractor_type = 'ArticleExtractor'
'''
    DefaultExtractor
    ArticleExtractor
    ArticleSentencesExtractor
    KeepEverythingExtractor
    KeepEverythingWithMinKWordsExtractor
    LargestContentExtractor
    NumWordsRulesExtractor
    CanolaExtractor
'''

def html2text_bp(html):
    text = None
    try:
        extractor = Extractor(extractor=extractor_type, html=html)
        text = extractor.getText()
    except:
        traceback.print_exc()
    return text

def is_filter(text):
    #Return True is text should be filtered
    #Filter if: text is not English
    try:
        lang = detect(text)
        if lang != "en":
            return True
        else:
            return False
    except:
        print "TEXT=" + text
        traceback.print_exc()
        return False
    return True

def extract_non_recipe(data):
    #Return None if data contain recipe schema
    #Otherwises extract text and return a json object that contains text 
    try:
        if 'html' in data:
            html = data['html']
        else:
            html = data['text']
        schema_match = RECIPE_SCHEMA.search(html)
        if schema_match == None:
            text = html2text_bp(html)
            if text:
                if not is_filter(text):
                    data['text'] = text
            else:
                return None
        else:
            return None
    except:
        traceback.print_exc()
        return None
    return data

def extract(data):
    #return a json object that contains text. 
    #if the extraction fails, return only the json object with the url,
    try:
        if 'html' in data:
            html = data['html']
        else:
            html = data['text']
        text = html2text_bp(html)
        if text:
            if not is_filter(text):
                data['text'] = text
        else:
            return None
    except:
        traceback.print_exc()
        return None
    return data
'''
#It is likely that python-boilerpipe does not work well with multi-process
def extract(indir, outdir):
    if not os.path.exists(outdir): 
        os.makedirs(outdir)

    #Default
    PROCESS_NUMBER = 1
    files = os.listdir(indir)
    for f in files:
        if f.split(".")[-1] != "json":
            continue
        print "Processing " + f
        p = Pool(PROCESS_NUMBER)
        args = []
        fpath = indir + "/" + f
        with open(fpath) as lines:
            for line in lines:
                try:
                    jsondata = json.loads(line)
                    args.append(jsondata)
                except:
                    traceback.print_exc()
                    continue
        print " Loaded " + f + ", Number of objects: " + str(len(args))
        out = open(outdir + "/" + f, "w")
        results = p.map(extract_process, args)
        for result in results:
            out.write(json.dumps(result) + "\n")
        out.close()
'''

def run_extract(indir, outdir):
    if not os.path.exists(outdir): 
        os.makedirs(outdir)

    #Default
    files = os.listdir(indir)
    count = 0
    for f in files:
        results = []
        if f.split(".")[-1] != "json":
            continue
        print "Processing " + f
        fpath = indir + "/" + f
        with open(fpath) as lines:
            for line in lines:
                count += 1 
                try:
                    jsondata = json.loads(line)
                    result = extract_non_recipe(jsondata)
                    #result = extract(jsondata)
                    if result:
                        results.append(result) 
                    if count % 10 == 0:
                        print " Processed " + str(count)
                except:
                    traceback.print_exc()
                    continue
        out = open(outdir + "/" + f, "w")
        for result in results:
            out.write(json.dumps(result) + "\n")
        out.close()


if __name__=="__main__":
    argv = sys.argv[1:]
    if len(argv) == 0:
        print "Args: [Input Directory] [Output Directory]"     
        print "[Input Directory]: Directory that contains html pages"
        print "[Output Directory]: Empty directory - if not existed, it will be created automatically"
        sys.exit(1)

    indir = argv[0]
    outdir = argv[1]
    run_extract(indir, outdir)
