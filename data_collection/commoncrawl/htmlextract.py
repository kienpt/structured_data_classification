#!/usr/bin/python
# author: Tuan-Anh Hoang-Vu (tuananh@nyu.edu)

import html5lib
from HTMLParser import HTMLParser
unescape = HTMLParser().unescape
from BeautifulSoup import BeautifulSoup
import sys

class HTMLExtract(object):
    def __init__(self):
        self.tree = None
        self.tags = []
        self.ignore_tags = []
        pass 

    def parse(self, location, encoding=None):
        dom_builder = html5lib.treebuilders.getTreeBuilder("dom")
        parser = html5lib.HTMLParser(tree=dom_builder)
        self.tree = parser.parse(location, encoding=encoding)

    def parse_unescape(self, location, encoding=None):
        dom_builder = html5lib.treebuilders.getTreeBuilder("dom")
        parser = html5lib.HTMLParser(tree=dom_builder)
        try:
            location = unescape(location)
        except:
            try:
                location = BeautifulSoup(location, convertEntities=BeautifulSoup.HTML_ENTITIES)
            except:
                pass
        # self.tree = parser.parse(unescape(location), encoding=encoding)
        try:
            self.tree = parser.parse(location.strip(), encoding=encoding)
        except:
            pass
            # print location

    def extract(self, tags, ignore_tags):
        self.tags = tags
        self.ignore_tags = ignore_tags
        contents = _extract_deduplicate(self.tree, self.tags, self.ignore_tags)
        return contents

    def cleanup(self):
        self.tree = None
        self.tags = []
        self.ignore_tags = []

def _extract(e, tags, ignore_tags, ignore_text=True):
    #This function return duplicated text
    results = []
    if e is None:
        return results
    if e.nodeType == e.TEXT_NODE and not ignore_text:
        text = e.nodeValue.strip()
        # print 'text', text
        if text is not None and text != '':
            results.append(text)
    elif e.nodeType == e.ELEMENT_NODE:
        # print e.tagName 
        if e.tagName in tags:
            text = _extract_text(e)
            # print 'element', text
            if text is not None and text != '':
                results.append(text)
            if len(e.childNodes) > 0:
                for child in e.childNodes:
                    results.extend(_extract(child, tags, ignore_tags, False))
        elif e.tagName not in ignore_tags:
            for child in e.childNodes:
                results.extend(_extract(child, tags, ignore_tags))
    else:
        for child in e.childNodes:
            results.extend(_extract(child, tags, ignore_tags))

    return results

def _extract_text(e):
    text = None
    if text is None or text == '':
        try:
            text = e.nodeValue.strip()
        except:
            pass
    if text is None or text == '':
        try:
            text = e.firstChild.nodeValue.strip()
        except:
            pass
    return text

def _extract_deduplicate(e, tags, ignore_tags, ignore_text=True):
    #Since _extract return duplicated results, this function removes the duplication while preserving the order of the text
    results = _extract(e, tags, ignore_tags, ignore_text=True)
    array_results = []
    set_results = set([])
    for s in results:
        if s not in set_results:
            array_results.append(s)
            set_results.add(s)
    return array_results

def test_extract(url):
    import requests
    res = requests.get(url)
    if res.status_code != 200:
        return 
    content = res.text
    e = HTMLExtract()
    e.parse(content)
    sentences = e.extract(set(['p', 'li', 'span', 'div', 'h1', 'h2', 'h3', 'h4', 'td', 'small', 'em', 'strong', 'b', 'i']), set(['script', 'style', 'noscript']))
    for s in sentences:
        s = s.encode('utf-8')
        print s
    e.cleanup()

if __name__ == '__main__':
    url = sys.argv[1]
    test_extract(url)
    
