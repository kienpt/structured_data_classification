#!/usr/bin/python
# author: Tuan-Anh Hoang-Vu (tuananh@nyu.edu)

import html5lib
from HTMLParser import HTMLParser

unescape = HTMLParser().unescape

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

    def extract(self, tags, ignore_tags):
        self.tags = tags
        self.ignore_tags = ignore_tags
        contents = _extract(self.tree, self.tags, self.ignore_tags)
        return contents

    def cleanup(self):
        self.tree = None
        self.tags = []
        self.ignore_tags = []

def _extract(e, tags, ignore_tags, ignore_text=True):
    results = []
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
            if len(e.childNodes) > 1:
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

if __name__ == '__main__':
    e = HTMLExtract()
    content = unescape(open('recipe.html').read())
    e.parse(content)
    sentences = e.extract(['p', 'li', 'span', 'div', 'h1', 'h2', 'h3', 'h4'], ['script', 'style', 'noscript'])
    for s in sentences:
        print s
    e.cleanup()