#!/bin/env
"""

definalize T-bars

we accidentally used the "final" flag on T-bars when we shouldn't have; undo that


djo, 9/14


"""

# ------------------------- imports -------------------------
import json
import sys

# ------------------------- script start -------------------------
if __name__ == '__main__':

    if len(sys.argv) < 3:
        print "usage: inputfile outputfile"
        sys.exit(1)

    bodylistfile = sys.argv[1]
    bookmarksfile = sys.argv[2]
    outputfilename = sys.argv[3]

    b = open(bodylistfile,'r+')
    lookup = {}
    for line in b:
        bodyID_chk = line.rstrip('\n')
        print "Screen for: " + bodyID_chk
        lookup[bodyID_chk] = 1
    
    #print "test: " + str(lookup['3529395'])

    jsondata = json.loads(open(bookmarksfile, 'rt').read())
    metadata = jsondata["metadata"]
    if metadata["description"] != "bookmarks":
        print "not a synpase annotation file!"
        sys.exit(1)
    if metadata["file version"] > 1:
        print "this file is from a newer Raveler than I can handle!"
        sys.exit(1)    
    
    new_bookmarks = []
    for bookmark in jsondata["data"]:
        bookmark_bodyID = str(bookmark["body ID"])
        #print "\tHereT: " + tbar_bodyID
        check_bookmark = lookup.get(bookmark_bodyID)
        #if lookup[tbar_bodyID] > 0:
        if check_bookmark:
            print "\tFoundT: " + bookmark_bodyID
            new_bookmarks.append(bookmark)
            continue

    jsondata["data"] = new_bookmarks
    
    for bookmark in jsondata["data"]:
        this_bodyID = str(bookmark["body ID"])
        print "\tNew: " + this_bodyID

    with open(outputfilename, 'wt') as f:
        json.dump(jsondata, f, indent=2)
