import sys
import os
import json
from multiprocessing import Process
import traceback

sys.path.append(os.path.dirname(__file__) + "/common")
sys.path.append("common")
from boilerpipe.extract import Extractor

extractor_type = 'DefaultExtractor'
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

def extract_process(filenames, indir, outdir):
    
    for f in filenames:
        infile = indir + "/" + f
        outfile = outdir + "/" + f
        out = open(outfile, "w")
        with open(infile) as lines:
            for line in lines:
                try:
                    data = json.loads(line)
                    html = data['text']
                    text = html2text(html)
                    if text:
                        js = {}
                        js['url'] = data['url']
                        js['text'] = text
                        out.write(json.dumps(js) + "\n")
                except:
                    traceback.print_exc()
        out.close()

def extract(indir, outdir):
    if not os.path.exists(outdir): 
        os.makedirs(outdir)

    #Default
    PROCESS_NUMBER = 8

    jobs = []
    files = os.listdir(indir)
    queues = []

    #Assign files to each process
    for i in range(PROCESS_NUMBER):
        q = []
        for j in range(i, len(files), PROCESS_NUMBER):
            q.append(files[j])
        queues.append(q)
    for q in queues:
        p = Process(target=extract_process, args=(q, indir, outdir))
        jobs.append(p)
        p.start()
    for p in jobs:
        p.join()


def html2text(html):
    text = None
    try:
        extractor = Extractor(extractor=extractor_type, html=html)
        text = extractor.getText()
    except:
        traceback.print_exc()
    return text

if __name__=="__main__":
    indir = sys.argv[1]
    outdir = sys.argv[2]
    extract(indir, outdir)
