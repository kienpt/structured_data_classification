import sys
sys.path.append("common")
from urlutility import URLUtility 
ext_blacklists = ["vn", "br", "it", "de", "fr", "ru", "jp", "pl", "nl"]

def is_filter(url, blacklists, counter):
    #blacklists contains list of hosts
    host = URLUtility.get_host(url) 
    ext = host.strip("/").split(".")[-1] 
    if ext in ext_blacklists:
        return True

    if "?" in host:
        return True
    if "=" in host:
        return True

    max = 1000
    if host in counter:
        counter[host] += 1
        if counter[host] >= max:
            blacklists.add(host)
    else:
        counter[host] = 1

    if host in blacklists:
        return True
    else:
        return False

def load_blacklist(f):
    bl = set()
    with open(f) as lines:
        for line in lines:
            line = line.strip().lower()
            host = URLUtility.get_host(line)
            print host
            bl.add(host)
    return bl

def run_filter(infile, outfile):
    blacklists = load_blacklist("blacklist.txt")
    out = open(outfile, "w")
    counter = {}
    with open(infile) as lines:
        for line in lines:
            url = line.strip()
            if is_filter(url, blacklists, counter):
                continue
            else:
                host = URLUtility.get_host(url)

                out.write(line)
    out.close()


if __name__=="__main__":
    infile = sys.argv[1]
    outfile = sys.argv[2]
    run_filter(infile, outfile)
