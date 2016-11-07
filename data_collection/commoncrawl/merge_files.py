'''
Merge commoncrawl data to smaller number of files, avoiding inodes problem
'''
import os

N = 120 #Number of merged files

def merge(indir, outdir):
    files = os.listdir(indir)
    x = len(files)/N #number of files per merged file
    c = 0
    out = None
    for f in files:
        if f.split(".")[-1] != "json":
            continue
        infile = indir + "/" + f
        if c%x == 0:
            if out:
                out.close()
            outfile = outdir + "/html_" + str(c/x) + ".json"
            out = open(outfile, "w")
        out.write(open(infile).read())
        c += 1



merge("alltypes_html", "html")
