import os 
import sys
import json
sys.path.append(os.path.dirname(__file__) + "../dmoz/common")
from urlutility import URLUtility 

def deduplicate(outfile, indirs):
    writer = open(outfile, 'w')
    cached_urls = set()
    for indir in indirs:
        for fname in os.listdir(indir):
            print "Reading", indir+'/'+fname
            for line in open(indir+'/'+fname):
                data = json.loads(line)
                url = URLUtility.normalize(data['url'])
                if url in cached_urls: 
                    continue
                cached_urls.add(url)
                writer.write(line)

if __name__ == '__main__':
    deduplicate(sys.argv[1], sys.argv[2:])