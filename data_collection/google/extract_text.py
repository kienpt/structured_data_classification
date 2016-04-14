#!/usr/bin/python
# author: Tuan-Anh Hoang-Vu (tuananh@nyu.edu)

import os
import sys
import json
from multiprocessing import Pool, cpu_count
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from news_extract import Extract
ex = Extract()

def extract_text(files):
    infile = files[0]
    outfile = files[1]
    print "Processing", infile
    writer = open(outfile, 'w')
    for line in open(infile):
        data = json.loads(line)
        content = ex.extract(data['text'])
        if content is not None:
            data['extract_text'] = content[2]
        else:
            data['extract_text'] = ''
        writer.write(json.dumps(data)+'\n')
    pass

if __name__ == '__main__':
    indir = sys.argv[1]
    outdir = sys.argv[2]
    os.mkdir(outdir)
    infiles = [indir+'/'+x for x in os.listdir(indir)]
    outfiles = [outdir+'/'+x for x in os.listdir(indir)]
    args = zip(infiles, outfiles)
    p = Pool(cpu_count())
    p.map(extract_text, args)
