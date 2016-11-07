'''
Count the number of high level domains from list of urls
'''
import sys
import json
sys.path.append("common")
from urlutility import URLUtility

def count(infile):
    sites = set([])
    with open(infile) as lines:
        for line in lines:
            obj = json.loads(line)
            url = obj['url']
            site = URLUtility.get_host(url)
            sites.add(site)
    for site in sites:
        print site
    print len(sites)

if __name__=="__main__":
    infile = sys.argv[1]
    count(infile)
