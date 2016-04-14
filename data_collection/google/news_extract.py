#!/usr/bin/python
# author: Tuan-Anh Hoang-Vu (tuananh@nyu.edu)

import warnings
warnings.filterwarnings("ignore", category=FutureWarning) 

import readability
import os
import sys
from readability.readability import Document
import re
import time
import dateutil.parser
from itertools import chain

TITLE_THRESHOLD = 100
# Add more strings that confuse the parser in the list
UNINTERESTING = set(chain(dateutil.parser.parserinfo.JUMP, 
                          dateutil.parser.parserinfo.PERTAIN,
                          ['a']))

def _get_date(tokens):
    for end in xrange(len(tokens), 0, -1):
        region = tokens[:end]
        if all(token.isspace() or token in UNINTERESTING
               for token in region):
            continue
        text = ''.join(region)
        try:
            date = dateutil.parser.parse(text)
            return end, date, len(text)
        except ValueError:
            pass
        except TypeError:
            pass
        except OverflowError:
            pass

def find_dates(text, max_tokens=10, allow_overlapping=False):
    tokens = filter(None, re.split(r'(\S+|\W+)', text))
    skip_dates_ending_before = 0
    for start in xrange(len(tokens)):
        region = tokens[start:start + max_tokens]
        result = _get_date(region)
        if result is not None:
            end, date, length = result
            if allow_overlapping or end > skip_dates_ending_before:
                skip_dates_ending_before = end
                yield date, length

class Extract:
    def __init__(self):
        #For remove HTML tag
        self.p = re.compile(r'<[^<]*?>')
        #For getting meta tags
        self.p2 = re.compile(r'<meta[^<]*?>')
        #For remove unused tags from body
        self.pb1 = re.compile(r'<noscript>.*?<\/noscript>', re.MULTILINE)
        self.pb2 = re.compile(r'<img.*?>', re.MULTILINE)
        self.pb3 = re.compile(r'<a.*?>.*?<\/a>', re.MULTILINE)
        self.pb4 = re.compile(r'<[^<]*?>')
    
    def extract(self, content):
        doc = Document(content)
        
        #Just to make sure it's welform
        try:
            body = doc.content()
        except:
            return None
            #It does not have content. Just ignore
        
        #Extract title
        try:
            title = doc.short_title()
        except:
            title = ""
        if title is "":
            return None

        #Extract article
        try:
            article = doc.summary()
        except:
            article = ""
        if article is "":
            return None

        #Need to clean HTML tag from article
        article = self.p.sub(' ', article)

        #Extract date
        '''
        Step to get correct date:
        1. Get from URL
        2. Get from Metadata
        3. Get from first body
        '''
        '''
        #2. Get from metadata
        metas = self.p2.findall(content)
        date2_candidates = []
        #Get content= from meta
        for meta in metas:
            p2s = re.compile(r'content="(.*?)"')
            met = p2s.search(meta)
            if met is None: continue
            if met.group(1) is None: continue
            try:
                date = dateutil.parser.parse(met.group(1))
                date2_candidates.append((date, len(met.group(1))))
            except ValueError:
                pass
            except TypeError:
                pass
        '''
        #3. Get from first body
        body = self.pb1.sub('', body)
        body = self.pb2.sub('', body)
        body = self.pb3.sub('', body)
        body = self.pb4.sub(' ', body)
        body = " ".join(body.split())
        title_fixed_whitespaces = " ".join(title.split())
        title_fixed_whitespaces = title_fixed_whitespaces[:50]
        mid_point = body.find(title_fixed_whitespaces)
        '''
        Little trick for WordPress title
        '''
        if mid_point == -1:
            title_fixed_whitespaces = title_fixed_whitespaces.replace("'", "&#8217;")
            mid_point = body.find(title_fixed_whitespaces)

        #start_point
        start_point = mid_point - TITLE_THRESHOLD
        if start_point < 0:
            start_point = 0
        #end_point
        end_point = mid_point + len(title_fixed_whitespaces) + TITLE_THRESHOLD
        if end_point > len(body):
            end_point = len(body)
        #Find the date
        max_length = 0
        date3 = None
        date3_candidates = find_dates(body[start_point:end_point])
        for dat3 in date3_candidates:
            if dat3[1] > max_length:
                date3 = dat3[0]

        #4. Select the best date
        date = date3
        
        #Return a tuple
        return (title, date, article)

#Debug
'''
start_time = time.time()

ex = Extract()
f = open(sys.argv[2])
content = f.read()
results = ex.extract(content)

if sys.argv[1] == "title":
    print results[0]
if sys.argv[1] == "content":
    print results[2]
if sys.argv[1] == "date":
    print results[1]
    
#End
print "Total time: " + str(time.time() - start_time)
'''
