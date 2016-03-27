'''
@author: Kien Pham (kienpt.vie@gmail.com)
@date: 02/26/2016
'''

import urllib2
import sys
import re
import urlparse

class HTMLParser:
    LINK_PATTERN = re.compile(r'href="(.*?)"')    
    END_PATTERN = re.compile('.*?\.(pdf|jpg|png|mp4|mp3|wmv|css|ico|xml|txt|json|svg)$')
    FILTER_PATTERN = re.compile('\.(css|xml)')
    @staticmethod
    def validate_link(link):
        '''
        - Filter css, js, media files (pdf, jpg, png, etc.)
        - Validate the url
        Return None if link should be filtered or invalid.
        '''
        link = link.lower()
        match = HTMLParser.FILTER_PATTERN.search(link)
        if match != None:
            return None

        match = HTMLParser.END_PATTERN.search(link)
        if match != None:
            return None

        if not link.startswith("http"):
            #Some link does not start with http, i.e mailto:
            return None

        link = link.split()[0] #If a link contains space, only keep the first part before the space

        return link
    
    @staticmethod
    def extract_links(url, html):
        '''
        Extract links from html source using regular expression
        Args:
            - url: url of the html source, used to construct absolute url from relative url
            - html: html source
        Returns:
            - links: extracted links
        '''
        match = HTMLParser.LINK_PATTERN.findall(html)
        links = set([])
        for link in match:
            link = urlparse.urljoin(url, link)
            link = HTMLParser.validate_link(link)
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
            link = urlparse.urljoin(url, link)
            link = HTMLParser.validate_link(link)
            if link:
                links.add(link)
        return list(links)

def test():
    print "test"

if __name__=="__main__":
    test()
