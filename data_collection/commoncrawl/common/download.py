'''
@author: Kien Pham (kienpt.vie@gmail.com)
@date: 03/25/2016
'''
import sys
import urllib2
from multiprocessing import Process
import requests
import os
from urlutility import URLUtility
import json
import traceback

requests.packages.urllib3.disable_warnings()

class Download:
    header = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36'}
    
    @staticmethod
    def collect_crawled_urls(output_dir):
        '''
        Collect all urls in output_dir
        Returns:
            - urls: list of urls
        '''
        urls = set([])
        files = os.listdir(output_dir)
        for f in files:
            filename = output_dir + "/" + f
            with open(filename) as lines:
                for line in lines:
                    try:
                        data = json.loads(line)
                        url = data["url"]
                        urls.add(url)
                    except:
                        print "Error while reading json line"
                        continue
            print "Finished reading " + filename
        return urls 

    @staticmethod
    def save_content(url, text, content_file):
        data = {}
        data["url"] = url
        text = text.encode('utf-8')
        data['text']  = text
        json.dump(data, content_file)
        content_file.write("\n")

    @staticmethod
    def crawlprocess(urls, start, output_dir, step):
        content_file = open(output_dir  + "/html_" + str(start) + ".json", "a+")
            
        for i in range(start, len(urls), step):
            url = urls[i]
            try:
                res = requests.get(url, headers=Download.header, verify=False, timeout=5)
                if res.status_code == 200:
                    Download.save_content(url, res.text, content_file)
            except Exception:
                #traceback.print_exc()                
                continue
        content_file.close()


    @staticmethod
    def download(urls, output_dir, PROCESS_NUMBER=64, recrawl=5):
        '''
        Download all urls in the url list and save the html content to output_dir
        Use multi-process to speed up the download
        Args:
            - urls: list of urls to be downloaded
            - output_dir: directory to save html 
        '''
        PROCESS_NUMBER = 32
        recrawl = 3
        print "Total number of urls to be crawled: " + str(len(urls))
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        jobs = []
        for i in range(PROCESS_NUMBER):
            p = Process(target = Download.crawlprocess, args = (urls, i, output_dir, PROCESS_NUMBER))
            jobs.append(p)
            p.start()
        for p in jobs:
            p.join()

        if recrawl > 1:
            recrawl = recrawl - 1 
            crawled_urls = Download.collect_crawled_urls(output_dir)
            print "Total number of crawled urls: " + str(len(crawled_urls))
            left_urls = [] #urls have not yet crawled
            for url in urls:
                if url not in crawled_urls:
                    left_urls.append(url)
            Download.download(left_urls, output_dir, PROCESS_NUMBER, recrawl)

def run(infile, outdir):
    urls = set([])
    with open(infile) as lines:
        for line in lines:
            url = line.strip().split("\t")[0]
            url = URLUtility.normalize(url) 
            urls.add(url)
    urls = list(urls)
    Download.download(urls, outdir)

if __name__=="__main__":
    argv = sys.argv[1:]
    if len(argv) == 0:
        print "Args: [Input File] [Output Directory]"     
        print "[Input File]: File that contains urls"
        print "[Output Directory]: Name of output directory"
        sys.exit(1)

    run(argv[0], argv[1])
