from urlparse import urlparse
import os
import sys
import json
from multiprocessing import Pool, cpu_count

def extract_domains(fname):
    results = {}
    for line in open(fname):
        data = json.loads(line)
        domain = urlparse(data['url'])
        url = '{uri.scheme}://{uri.netloc}/'.format(uri=domain)
        try:
            results[url] += 1
        except:
            results[url] = 1
    return results

p = Pool(cpu_count()-1 or 1)
indir = sys.argv[1]
outfile = sys.argv[2]
fnames = [indir+'/'+x for x in os.listdir(indir)]
results = p.map(extract_domains, fnames)
domains = {}
for res in results:
    for k,v in res.iteritems():
        try:
            domains[k] += v
        except:
            domains[k] = v

writer = open(outfile, 'w')
for k,v in sorted(domains.iteritems(), key=lambda(k,v):(v,k), reverse=True):
    writer.write(k+'\n')