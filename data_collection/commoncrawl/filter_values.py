'''
Filter values from urls that are likely to be false positive.
For examples: let A is list of urls that contain either ingredients or instructions.
Any url is not in A is false positive or not considered in training and testing
'''
import json
import sys
import traceback

def load_urls(infile):
    print "Reading " + infile
    urls = set([])
    with open(infile) as lines:
        for line in lines:
            try:
                obj = json.loads(line)
                url = obj['url']
                urls.add(url)
            except:
                traceback.print_exc()
                print line
    print "Done Reading " + infile
    return urls

def filter_byfile(infile, gt_urls, outfile):
    out = open(outfile, "w")
    with open(infile) as lines:
        for line in lines:
            obj = json.loads(line)
            url = obj['url']
            if url in gt_urls:
                out.write(line)
    out.close()

def filter(args):
    print len(args)
    gt_files, filter_files, outdir = args
    gt_files = gt_files.split(",") 
    filter_files = filter_files.split(",")
    gt_urls = set([])
    for f in gt_files:
        urls = load_urls(f)
        gt_urls = gt_urls.union(urls)

    for f in filter_files:
        fname = f.split("/")[-1]
        outfile = outdir + "/filtered_" + fname 
        filter_byfile(f, gt_urls, outfile)

if __name__=="__main__":
    print "[f1,f2] [f1,f2,f3] [outdir]"
    filter(sys.argv[1:])
