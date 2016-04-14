'''
@author: Kien Pham (kienpt.vie@gmail.com)
@date: 02/19/2016
'''
import urllib2
from urlparse import urlparse
import re

class URLUtility:
    
    END_PATTERN = re.compile('.*?\.(pdf|jpg|png|mp4|mp3|wmv|css|ico|xml|txt|json|svg)$')
    FILTER_PATTERN = re.compile('\.(css|xml)')

    @staticmethod
    def decode(url):
        decoded_url = urllib2.unquote(url)
        return decoded_url

    @staticmethod
    def encode(url):
        return urllib2.quote(url).replace("/", "%2F")

    @staticmethod
    def is_same_site(url1, url2):
        '''
        Check whether two urls are in the same site
        REQUIREMENT: in order to be parsed, url1 and url2 must be normalized (see normalize())
        Returns:
            - True if two urls are in the same site, otherwises return False
        '''
        parsed_url1 = urlparse(url1)
        parsed_url2 = urlparse(url2)
        if parsed_url1.netloc == parsed_url2.netloc:
            return True
        else: 
            return False
        
    @staticmethod
    def validate_link(link):
        '''
        - Filter css, js, media files (pdf, jpg, png, etc.)
        - Validate the link

        Returns: 
            - None if link should be filtered or invalid.
        '''
        try:        
            link = link.lower()

            #Remove link that does not point to html page 
            match = URLUtility.FILTER_PATTERN.search(link)
            if match != None:
                return None
            match = URLUtility.END_PATTERN.search(link)
            if match != None:
                return None

            #Remove link that does not start with http, i.e mailto:
            if not link.startswith("http"):
                return None

            return link
        except:
            print "URL can not be validated: " + str(url)
            return None

    @staticmethod
    def get_host(url):
        '''
        Extract the high level domain from an NORMALIZED url
        '''
        parsed_uri = urlparse(url)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        return domain

    @staticmethod
    def normalize(url):
        '''
        Normalize urls to this format: http://www.website.domain (in lower cases) 
        NOTE: This is not a standard way to normalize url, see: https://docs.python.org/2/library/urlparse.html

        Args:
            url - an input url 
        Returns:
            norm_url - a normalized url with lower cases. Format: http://www.website.domain 
            Return None if unsuccessful
        '''
        #Extract network location
        try:
            url = url.lower()
            #Remove the part after '#' i.e http://abc.com/index.html#abcd -> http://abc.com/index.html
            if '#' in url:
                url = url.split("#")[0]
            url = url.strip("/")
            url = url.split()[0] #If a link contains space, only keep the first part before the space
            

            if len(url) > 8:
                if url[:7] == 'http://':
                    url = url[7:]
                elif url[:8] == 'https://':
                    url = url[8:]

            #Remove www from network location
            if len(url) > 4:
                if url[:4] == 'www.':
                    url = url[4:]

            url = "http://www." + url
            return url
        except:
            print "url can not be normalized: " + str(url)
            return None

def test():
    u = 'nYu.edu'
    print "URL: " + u
    u = URLUtility.normalize(u)
    print "After normalization: " + u
    u = URLUtility.encode(u)
    print "After encoding: " + u
    u = URLUtility.decode(u)
    print "After decoding: " + u

#if __name__=="__main__":
#    test()
