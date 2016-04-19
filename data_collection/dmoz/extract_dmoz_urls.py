import sys
import re

'''
Given topics, collect urls from DMOZ
Usage:
    [topic_file] [output_file]
'''

dmoz = "content.rdf.u8"
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
    argv = sys.argv[1:]
    if len(argv) == 0:
        print "Args: [Topic File] [Output File]"     
        print "[Topic File]: File that contains list of topic"
        print "[Output File]: Name of the output file"
        sys.exit(1)
   
    topicfile = argv[0]
    outfile = argv[1]
    topics = read_topics(topicfile)
    get_links(outfile, topics)
