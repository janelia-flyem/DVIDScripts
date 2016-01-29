#!/bin/env
"""

definalize T-bars

we accidentally used the "final" flag on T-bars when we shouldn't have; undo that


djo, 9/14


"""

# ------------------------- imports -------------------------
import json
import sys
import urllib

# ------------------------- script start -------------------------
if __name__ == '__main__':
    
    if len(sys.argv) < 3:
        print "usage: inputfile outputfile"
        sys.exit(1)

    inputfilename = sys.argv[1]
    outputfilename = sys.argv[2]
    dvid_server = sys.argv[3]
    dvid_uuid = sys.argv[4]
    labelblk = sys.argv[5]

    #y_adjust = int(sys.argv[3])
    # not much validation here!
    jsondata = json.loads(open(inputfilename, 'rt').read())
    metadata = jsondata["metadata"]
    if metadata["description"] != "bookmarks":
        print "not a bookmarks file!" 
        sys.exit(1)
    if metadata["file version"] > 1:
        print "this file is from a newer Raveler than I can handle!"
        sys.exit(1)

    proxies = {'http': 'http://' + dvid_server + '/'}

    for bookmark in jsondata["data"]:
        #synapse["T-bar"]["status"] = "working"
        bkm_location = bookmark["location"]
        bkm_bodyID = bookmark["body ID"]
        print "bkm_x: " + str(bkm_location[0])
        print "bkm_y: " + str(bkm_location[1])
        print "bkm_z: " + str(bkm_location[2])
        bkm_location = str(bkm_location[0]) + "_" + str(bkm_location[1]) + "_" + str(bkm_location[2])
        dvid_request_bkm = "http://" + dvid_server + "/api/node/" + dvid_uuid + "/" +  labelblk + "/label/" + bkm_location
        print "dvid_url: " + dvid_request_bkm
        response = urllib.urlopen(dvid_request_bkm, proxies=proxies).read()
        labeldata = json.loads(response)
        print "Cur body ID: " + str(bkm_bodyID)
        print "New body ID: " + str(labeldata["Label"])
        bookmark["body ID"] = labeldata["Label"]

            
    with open(outputfilename, 'wt') as f:
        json.dump(jsondata, f, indent=2)


