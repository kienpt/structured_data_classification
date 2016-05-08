import json
import sys

fin = open(sys.argv[1])
fout = open(sys.argv[2], 'w')

for line in fin:
    data = json.loads(line.strip())
    if data is not None:
        items = data['items']
        for item in items:
            fout.write(item['link']+'\n')
            fout.flush()