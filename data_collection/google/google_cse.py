import requests
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
import json
import time
from config import *

def get_results(query, start=1):
    r = requests.get('https://www.googleapis.com/customsearch/v1?key='+api_key+'&cx='+cse_uid+'&q='+query+'&start='+str(start))
    if r.status_code == 200:
        return r.json()
    else:
        print r.text
        return None

# print get_results('pizza')

fout = open('results.json', 'w')

keywords = map(str.strip, open('keywords.txt').readlines())
for i in range(4,8):
    start = 1+i*10
    for q in keywords:
        print "Querying", q, "and start =", start
        data = get_results(q, start)
        # data = {'q':q, 'start':start}
        fout.write(json.dumps(data) + '\n')
        fout.flush()
        time.sleep(1)