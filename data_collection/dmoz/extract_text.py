import sys
import os
import json
from multiprocessing import Process
import traceback

sys.path.append(os.path.dirname(__file__) + "/common")
sys.path.append("common")
from boilerpipe.extract import Extractor
from bs4 import BeautifulSoup

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
                    print "before"
                    print data['url']
                    print data['text']
                    text = html2text_bp(html)
                    print "after"
                    if text:
                        print text
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
    PROCESS_NUMBER = 1

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


def html2text_bp(html):
    text = None
    try:
        extractor = Extractor(extractor=extractor_type, html=html)
        text = extractor.getText()
    except:
        traceback.print_exc()
    return text

def html2text_bs(html):
    text = None
    try:
        soup = BeautifulSoup(html)
        text = soup.get_text()
    except:
        traceback.print_exc()
    return text

if __name__=="__main__":
    argv = sys.argv[1:]
    if len(argv) == 0:
        print "Args: [Input Directory] [Output Directory]"     
        print "[Input Directory]: Directory that contains html pages"
        print "[Output Directory]: Empty directory - if not existed, it will be created automatically"
        sys.exit(1)

    indir = argv[0]
    outdir = argv[1]
    extract(indir, outdir)
