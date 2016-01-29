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
    annotsynapsefile = sys.argv[2]
    outputfilename = sys.argv[3]

    b = open(bodylistfile,'r+')
    lookup = {}
    for line in b:
        bodyID_chk = line.rstrip('\n')
        print "Screen for: " + bodyID_chk
        lookup[bodyID_chk] = 1
    
    #print "test: " + str(lookup['3529395'])

    jsondata = json.loads(open(annotsynapsefile, 'rt').read())
    metadata = jsondata["metadata"]
    if metadata["description"] != "synapse annotations":
        print "not a synpase annotation file!"
        sys.exit(1)
    if metadata["file version"] > 1:
        print "this file is from a newer Raveler than I can handle!"
        sys.exit(1)    
    
    new_synapses = []
    for synapse in jsondata["data"]:
        #synapse["T-bar"]["status"] = "working"
        tbar_location = synapse["T-bar"]["location"]
        tbar_bodyID = str(synapse["T-bar"]["body ID"])
        #print "\tHereT: " + tbar_bodyID
        check_tbar = lookup.get(tbar_bodyID)
        #if lookup[tbar_bodyID] > 0:
        if check_tbar:
            print "\tFoundT: " + tbar_bodyID
            new_synapses.append(synapse)
            continue
        for psd in synapse["partners"]:
            psd_location = psd["location"]
            psd_bodyID = str(psd["body ID"])
            #print "\tHereP: " + psd_bodyID
            check_psd = lookup.get(psd_bodyID)
            if check_psd:
                print "\tFoundP: " + psd_bodyID
                new_synapses.append(synapse)
                continue

    jsondata["data"] = new_synapses
    
    for synapse in jsondata["data"]:
        tbar_bodyID = str(synapse["T-bar"]["body ID"])
        print "\tNew: " + tbar_bodyID

    with open(outputfilename, 'wt') as f:
        json.dump(jsondata, f, indent=2)
