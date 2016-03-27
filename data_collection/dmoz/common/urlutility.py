'''
@author: Kien Pham (kienpt.vie@gmail.com)
@date: 02/19/2016
'''
import urllib2
from urlparse import urlparse
class URLUtility:
    @staticmethod
    def decode(url):
        decoded_url = urllib2.unquote(url)
        return decoded_url

    @staticmethod
    def encode(url):
        return urllib2.quote(url).replace("/", "%2F")

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
        '''
        #Extract network location
        norm_url = url.lower()
        if len(norm_url) > 8:
            if norm_url[:7] == 'http://':
                norm_url = norm_url[7:]
            elif norm_url[:8] == 'https://':
                norm_url = norm_url[8:]

        #Remove www from network location
        if len(norm_url) > 4:
            if norm_url[:4] == 'www.':
                norm_url = norm_url[4:]

        norm_url = "http://www." + norm_url
        return norm_url

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
