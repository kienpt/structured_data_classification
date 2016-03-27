'''
This script downloads the urls and extract the outlinks within the corresponding sites.
Usage:
    [urls_file] [output_file]
'''
import sys
import requests
sys.path.append("common")
from urlutility import URLUtility 
from download import Download
from htmlparser import HTMLParser
import os
import json

def expand(urls_file, output_file):
    out = open(output_file, "w") 
    html_dir = "html" 
    
    #Copy urls from urls_file to output_file
    with open(urls_file) as lines:
        for line in lines:  
            out.write(line)

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
    Download.download(urls, html_dir)
    files = os.listdir(html_dir)
    for f in files:
        filename = html_dir + "/" + f
        with open(filename) as lines:
            for line in lines:
                data = json.loads(line)
                url = data['url']
                html_content = data['text'] 
                #links = HTMLParser.extract_links(url, html_content)
                links = HTMLParser.extract_links_bs(url, html_content)
                for link in links:
                    out.write(link.encode('utf-8') + "\n") 
    out.close()

if __name__=="__main__":
    urls_file = sys.argv[1]
    output_file = sys.argv[2]
    expand(urls_file, output_file)
