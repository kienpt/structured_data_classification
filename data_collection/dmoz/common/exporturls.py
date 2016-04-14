import os
import json
from urlutility import URLUtility 
import sys

class ExportURL:

    @staticmethod
    def load_urls(indir):
        '''
        Return urls from all files in indir directory
        '''
        urls = set([]) #return
        files = os.listdir(indir)
        for f in files:
            filename = indir + "/" + f
            with open(filename) as lines:
                for line in lines:
                    data = json.loads(line)
                    url = data['url']
                    urls.add(url)
    
        return list(urls)
    
    @staticmethod
    def export_urls(indir, outfile):
        urls = ExportURL.load_urls(indir)
        out = open(outfile, "w")
        for url in urls:
            out.write(url + "\n")
        out.close()

    @staticmethod
    def export_host(indir, outfile):
        urls = ExportURL.load_urls(indir)
        uniq_hosts = set([])
        out = open(outfile, "w")
        for url in urls:
            host = URLUtility.get_host(url)
            out.write(url + "\n")
        out.close()
       
def main(argv):
    indir = argv[0]
    outfile = argv[1]
    if len(argv) == 3:
        if argv[2] == "h":
            ExportURL.export_host(indir, outfile)
    else:
        ExportURL.export_urls(indir, outfile)

if __name__=="__main__":
    main(sys.argv[1:])
