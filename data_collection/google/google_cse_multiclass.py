import requests
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
import json
import time
from config import *

def get_results(cse_uid, query, start=1):
    url = 'https://www.googleapis.com/customsearch/v1?key='+api_key+'&cx='+cse_uid+'&q='+query+'&start='+str(start)
    # print url
    # return url
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    else:
        print r.text
        return None

cse_uids = map(str.strip, open('cse.txt').readlines())
cse_uids = [x.split(':') for x in cse_uids]
cse_uids = {x[0]: x[1] for x in cse_uids}

keywords = map(str.strip, open('../dmoz/data/alltopics_splitted.txt').readlines())
keywords = [x.split(',') for x in keywords]
keywords = {x[0].replace(' ', ''):x for x in keywords}

for topic, uid in cse_uids.iteritems():
    fout = open('data/'+topic.lower()+'.json', 'w')
    kws = keywords[topic]
    for i in range(0, 5):
        start = 1+i*10
        for q in kws:
            print "Querying", q, "and start =", start
            data = get_results(cse_uid+':'+uid, q, start)
            fout.write(json.dumps(data) + '\n')
            fout.flush()
            time.sleep(1)