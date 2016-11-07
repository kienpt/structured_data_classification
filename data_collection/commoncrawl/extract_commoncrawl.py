'''
This script collects webpages that have schema.org objects from commoncrawl data
Parameters:
    [file that contains path to commoncrawl data: warc.paths] [output directory]
'''
import os
import traceback
import warc
import sys
import re
import json
import urllib2
import time
import requests
from multiprocessing import Pool, cpu_count

def encode(url):
    return urllib2.quote(url).replace("/", "%2F")

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

def parse_warc(filename, outdir):
    #Read warc file and return records that contain recipe in json format
    #Output: filename + ".json"

    TYPES = ['person','product','event','movie','restaurant','recipe','book','tvseries','softwareapplication','jobposting','drug']
    SCHEMAORG_PATTERN = generate_pattern(TYPES)

    outfile =  filename + ".json"
    out = open(outfile, "w")
    try:
        print "Processing " + filename
        fo = warc.open(filename)
        count = 0
        begin = time.time()
        for record in fo:
            try:
                count += 1
                html = record.payload.read()
                match_schema = SCHEMAORG_PATTERN.search(html)
                if match_schema:
                    url = record['WARC-Target-URI']
                    try:
                        html = unicode(html, errors='replace')                        
                        obj = {}
                        obj['url'] = url
                        obj['html'] = html
                        json.dump(obj, out)
                        out.write("\n")
                    except:
                        obj = {}
                        obj['url'] = url
                        obj['html'] = html.decode('utf-8')
                        json.dump(obj, out)
                        out.write("\n")
                '''
                #debug
                if count %1000 == 0:
                    end = time.time()
                    print " Processed " + str(count) + " records in " +  str(end-begin)
                    begin = time.time()
                '''
            except:
                traceback.print_exc()
                continue
    except:
        print "Failed to parse " + filename
    out.close()

def download(url, outdir):
    try:
        #Download the url and save to outdir directory
        #Return name of the saved file
        filename = outdir + "/" + encode(url)
        if os.path.isfile(filename):
            return filename
        # NOTE the stream=True parameter
        print "Downloading " + filename
        r = requests.get(url, stream=True)
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024000): 
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
    except:
        print "Download Failed: " + filename
        traceback.print_exc()
    return filename

def clean(infile, outdir):
    #Remove files that haven't finished downloading (gz files) and processing (corresponding json files)
    #Return list of not-processed gz files (This files will not be downloaded and processed again)
    processed_gzfiles = set([])
    files = os.listdir(outdir)
    for f in files:
        if f.split(".")[-1] == "gz":
            gzfile = outdir + "/" + f
            print "CLEAN: Removing " + gzfile
            os.remove(gzfile)

            jsonfile = gzfile + ".json"
            if os.path.isfile(jsonfile):
                print "CLEAN: Removing " + jsonfile
                os.remove(jsonfile)

    for f in files:
        if f.split(".")[-1] == "json":
            gzfile = f.strip(".json")
            processed_gzfiles.add(gzfile)
            
    gzfiles = [] 
    with open(infile) as lines:
        for line in lines:
            url = "https://commoncrawl.s3.amazonaws.com/" + line.strip() 
            gzfile = encode(url)
            if gzfile not in processed_gzfiles:
                gzfiles.append(line.strip())
    return gzfiles 

def process(args):
    #Download then extract process
    filename, outdir = args
    url = "https://commoncrawl.s3.amazonaws.com/" + filename 
    filename = download(url, outdir)
    parse_warc(filename, outdir)
    print "FINISHED_PROCESS: Removing " + filename
    os.remove(filename)

def download_and_extract(infile, outdir):
    NUMBER_PROCESSES = 10
    p = Pool(NUMBER_PROCESSES)
    args = []
    gzfiles = clean(infile, outdir)
    print "Number of files left to extracted: " + str(len(gzfiles))
    if len(gzfiles) == 0:
        return False
    for gzfile in gzfiles:
        args.append([gzfile, outdir])
    results = p.map(process, args)

def main(argv):
    infile = argv[0] #file that contains path to commoncrawl data: warc.paths
    outdir = argv[1].strip("/") #output directory 
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    while True:
        try:
            cont = download_and_extract(infile, outdir)    
            if cont == False:
                return
        except:
            traceback.print_exc()
            continue

if __name__=="__main__":
    main(sys.argv[1:])
