import sys
import re

'''
Given topics, collect urls from DMOZ
Args:

Returns:
'''

dmoz = "structure.rdf.u8"
START = re.compile("<Topic r:id=\"(.*)\">")
END = re.compile("</Topic>")
LINK = re.compile("<link r:resource=\"(.*)\"></link>")

def read_topics(topicfile):
    '''
    Args:

    Returns:
    '''
    topics = set([])
    with open(topicfile) as lines:
        for line in lines:
            topic = line.strip("\n")
            topics.add(topic)
    return topics

def get_links(outfile, topics):
    '''
    Args:

    Returns:

    '''
    links = []
    inTopic = False
    rightTopic = False
    count = 0
    topic = ""
    out = open(outfile, "w")
    with open(dmoz) as lines:
        for line in lines:
            count += 1
            if (count % 1000000) == 0:
                print "Processing..." + str(count)
            if inTopic:
                END_match = END.search(line)
                if END_match:
                    inTopic = False
                    rightTopic = False
                else:
                    if rightTopic:
                        LINK_match = LINK.search(line)
                        if LINK_match:
                             out.write(LINK_match.group(1) + "\t" + topic + "\n")
            else:
                START_match = START.search(line)
                if START_match:
                    inTopic = True
                    topic = START_match.group(1)
                    for t in topics:
                        if (t in topic):
                            rightTopic = True
                            break
    out.close()

if __name__=="__main__":
    outfile = sys.argv[1]
    topicfile = "topics.txt" 
    topics = read_topics(topicfile)
    get_links(outfile, topics)
