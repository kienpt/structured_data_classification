'''
Collect the negative examples for recipe domain
'''
import sys
import requests
import os
sys.path.append(os.path.dirname(__file__) + "/common")
sys.path.append("common")
from urlutility import URLUtility 
from download import Download
from htmlparser import HTMLParser
import json
import traceback

def expand(indir, output_file):
    files = os.listdir(indir)
    uniq_links = set()#many seed urls come from the same site, so there exists duplicated outlinks from seed urls
    out = open(output_file, "w") 
    for f in files:
        if f.split(".")[-1] != "json":
            #make sure this is json file
            continue
        filename = indir + "/" + f
        with open(filename) as lines:
            for line in lines:
                try:
                    data = json.loads(line)
                    url = data['url']
                    url = URLUtility.normalize(url)
                    html_content = data['html'] 
                    #links = HTMLParser.extract_links(url, html_content)
                    links = HTMLParser.extract_links_bs(url, html_content)
                    for link in links:
                        if URLUtility.is_same_site(url, link):
                            if link not in uniq_links:
                                uniq_links.add(link)
                                out.write(link.encode('utf-8') + "\n")
                    if url not in links:
                        out.write(url.encode('utf-8') + "\n")
                except:
                    traceback.print_exc()
                    continue


def main(argv):
    indir = argv[0]
    output_file = argv[1]
    expand(indir, output_file)

if __name__=="__main__":
    main(sys.argv[1:])
