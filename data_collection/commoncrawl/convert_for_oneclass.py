import sys
import json
import traceback
import os

infile = sys.argv[1]
indir = sys.argv[2]
outfile = indir + "/" + infile
out = open(outfile, "w")

with open(infile) as lines:
    for line in lines:
        try:
            obj = json.loads(line)
            url, value = obj[0]
            data = {}
            data['url'] = url
            data['text'] = value
            out.write(json.dumps(data) + "\n")
        except:
            continue

out.close()
