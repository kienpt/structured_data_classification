'''
This script downloads the urls and extract the outlinks within the corresponding sites.
Usage:
    [urls_file] [output_file]
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

'''
def expand(urls_file, output_file):
    out = open(output_file, "w") 
    html_dir = "recipe" 
    if not os.path.exists(html_dir): 
        os.makedirs(html_dir)
    
    #Download and extract in-domain outlinks from urls_file
    url2topic = {}
    with open(urls_file) as lines:
        for line in lines:
            values = line.strip("\n").split("\t")
            url = URLUtility.normalize(values[0])
            if url in url2topic:
                continue
            if len(values) == 2:
                topic = values[1]
                url2topic[url] = topic
            else:
                url2topic[url] = ""

    urls = url2topic.keys()
    #Download.download(urls, html_dir)

    print "Download finished!"
    print "Extracting outlinks..."
'''

def expand(indir, output_file):
    files = os.listdir(indir)
    uniq_links = set()#many seed urls come from the same site, so there exists duplicated outlinks from seed urls
    out = open(output_file, "w") 
    for f in files:
        filename = indir + "/" + f
        with open(filename) as lines:
            for line in lines:
                data = json.loads(line)
                url = data['url']
                url = URLUtility.normalize(url)
                html_content = data['text'] 
                #links = HTMLParser.extract_links(url, html_content)
                links = HTMLParser.extract_links_bs(url, html_content)
                for link in links:
                    if URLUtility.is_same_site(url, link):
                        if link not in uniq_links:
                            uniq_links.add(link)
                            out.write(link.encode('utf-8') + "\n")
                if url not in links:
                    out.write(url.encode('utf-8') + "\n")
                    
    out.close()


if __name__=="__main__":
    indir = sys.argv[1]
    output_file = sys.argv[2]
    expand(indir, output_file)
