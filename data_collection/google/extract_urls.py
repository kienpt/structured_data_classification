import json

fin = open('results.json')
fout = open('urls.txt', 'w')

for line in fin:
    data = json.loads(line.strip())
    if data is not None:
        items = data['items']
        for item in items:
            fout.write(item['link']+'\n')
            fout.flush()