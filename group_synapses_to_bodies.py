#!/bin/env
"""
python version of group synapses

lau, 10/15

"""

# ------------------------- imports -------------------------
import json
import sys

# ------------------------- script start -------------------------
if __name__ == '__main__':

    if len(sys.argv) < 2:
        print "usage: <annotation synapse json> <output json>"
        sys.exit(1)

    annotsynapsefile = sys.argv[1]
    outputfilename = sys.argv[2]

    jsondata = json.loads(open(annotsynapsefile, 'rt').read())
    metadata = jsondata["metadata"]
    if metadata["description"] != "synapse annotations":
        print "not a synpase annotation file!"
        sys.exit(1)
    if metadata["file version"] > 1:
        print "this file is from a newer Raveler than I can handle!"
        sys.exit(1)

    group_synapses = {}

    for synapse in jsondata["data"]:
        #synapse["T-bar"]["status"] = "working"
        tbar_location = synapse["T-bar"]["location"]
        tbar_bodyID = str(synapse["T-bar"]["body ID"])
        #print "\tHereT: " + tbar_bodyID
        check_tbar = group_synapses.get(tbar_bodyID)
        #if lookup[tbar_bodyID] > 0:
        if check_tbar:
            #print "FoundT: " + tbar_bodyID
            group_synapses[tbar_bodyID]["synapse count"] += 1
            group_synapses[tbar_bodyID]["T-bar count"] += 1
            body_locations = group_synapses[tbar_bodyID]["locations"]
            body_locations.append(tbar_location)
        else:
            #print "NewT: " + tbar_bodyID
            this_hash = {}
            this_hash["synapse count"] = 1
            this_hash["T-bar count"] = 1
            this_hash["PSD count"] = 0
            this_location = []
            this_location.append(tbar_location)
            this_hash["locations"] = this_location
            group_synapses[tbar_bodyID] = this_hash

        for psd in synapse["partners"]:
            psd_location = psd["location"]
            psd_bodyID = str(psd["body ID"])
            #print "\tHereP: " + psd_bodyID
            check_psd = group_synapses.get(psd_bodyID)
            if check_psd:
                #print "\tFoundP: " + psd_bodyID
                group_synapses[psd_bodyID]["synapse count"] += 1
                group_synapses[psd_bodyID]["PSD count"] += 1
                body_locations = group_synapses[psd_bodyID]["locations"]
                body_locations.append(psd_location)
                #new_synapses.append(synapse)
            else:
                this_hash = {}
                this_hash["synapse count"] = 1
                this_hash["PSD count"] = 1
                this_hash["T-bar count"] = 0
                this_location = []
                this_location.append(psd_location)
                this_hash["locations"] = this_location
                group_synapses[psd_bodyID] = this_hash


    final_list = []
    #sorted(group_synapses, key=lambda i: group_synapses[i]["synapse count"])
    #for bodyID in group_synapses:
    thresh_hold_count = 0;
    for bodyID in sorted(group_synapses, key=lambda i: group_synapses[i]["synapse count"]):
        thresh_hold_count += 1
        total_synapses = group_synapses[bodyID]["synapse count"]
        total_tbars = group_synapses[bodyID]["T-bar count"]
        total_psds = group_synapses[bodyID]["PSD count"]        
        body_locations = group_synapses[bodyID]["locations"]
        num_bodies = len(body_locations)
        split_num = num_bodies/2;
        #print "Final: " + bodyID + " tbars:" + str(total_tbars) + " psds:" + str(total_psds) + " syns:" + str(total_synapses) + " locs:" + str(num_bodies) + " split:" + str(split_num)
        body_loc = body_locations[split_num]
        #print "\tx: " + str(body_loc[0])
        #print "\ty: " + str(body_loc[1])
        #print "\tz: " + str(body_loc[2])
        body_hash = {}
        body_hash["body ID"] = int(bodyID)
        body_hash["location"] = body_loc
        body_hash["body synapses"] = total_synapses
        body_hash["body T-bars"] = total_tbars
        body_hash["body PSDs"] = total_psds
        body_hash["body threshold"] = thresh_hold_count 
        body_hash["text"] = str(total_synapses) + " Synapses, " + str(total_tbars) + " T-bars, " + str(total_psds) + " PSDs"
        final_list.append(body_hash)
        #for body_loc in body_locations:
        #    print "\tx: " + str(body_loc[0])
        #    print "\ty: " + str(body_loc[1])
        #    print "\tz: " + str(body_loc[2])


    bookmark_template = "/groups/flyem/home/flyem/bin/json/annotation_bookmarks_template.json"
    outjsondata = json.loads(open(bookmark_template, 'rt').read())    
    outjsondata["data"] = final_list

    with open(outputfilename, 'wt') as f:
        json.dump(outjsondata, f, indent=2)
