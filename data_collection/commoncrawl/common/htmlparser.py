'''
@author: Kien Pham (kienpt.vie@gmail.com)
@date: 02/26/2016
'''

import urllib2
import sys
import re
import urlparse
from urlutility import URLUtility

class HTMLParser:
    LINK_PATTERN = re.compile(r'href="(.*?)"')    

    
    @staticmethod
    def extract_links(url, html):
        '''
        Extract links from html source using regular expression
        Args:
            - url: url of the html source, used to construct absolute url from relative url
            - html: html source
        Returns:
            - links: extracted (normalized and validated) links
        '''
        match = HTMLParser.LINK_PATTERN.findall(html)
        links = set([])
        for link in match:
            link = urlparse.urljoin(url, link)
            link = URLUtility.validate_link(link)
            if link:
                link = URLUtility.normalize(link)
                if link:
                    links.add(link)
        return list(links)

    @staticmethod
    def extract_links_bs(url, html):
        '''
        Extract links from html source using beautiful soup
        Args:
            - url: url of the html source, used to construct absolute url from relative url
            - html: html source
            - html: html source
        Returns:
            - links: extracted links
       
        '''
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html)
        links = set()
        for tag in soup.findAll('a', href=True):
            link = tag['href']
            try:
                link = urlparse.urljoin(url, link)
            except:
                continue
            link = URLUtility.validate_link(link)
            if link:
                link = URLUtility.normalize(link)
                if link:
                    links.add(link)
        return list(links)

def test():
    print "test"

if __name__=="__main__":
    test()
