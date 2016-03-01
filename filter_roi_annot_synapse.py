#!/bin/env
"""
Script that will select synapses that are either in a DVID ROI or outside the DVID ROI.

example:
select synapses inside glomerulus roi:
python filter_roi_annot_synapse.py feb24_annot_syn_dvid_ab0efglom_updated.json inside_glom.json emdata1:8500 f94a1 glomerulus 1

select synapses outside of glomerulus roi:
python filter_roi_annot_synapse.py feb24_annot_syn_dvid_ab0efglom_updated.json outside_glom.json emdata1:8500 f94a1 glomerulus 0

lau, 2/16

"""

# ------------------------- imports -------------------------
import json
import sys
import requests
import random
import os

# ------------------------- fuctions -------------------------

# ------------------------- script start -------------------------
if __name__ == '__main__':

    if len(sys.argv) < 6:
        print "usage: python filter_annot_synapse.py input_json output_json dvid_server dvid_uuid dvid_roi roi_select_toggle"
        sys.exit(1)

    annotsynapsefile = sys.argv[1]
    outputfilename = sys.argv[2]
    dvid_server = sys.argv[3]
    dvid_uuid = sys.argv[4]
    dvid_roi = sys.argv[5]
    roi_toggle = int(sys.argv[6])
    
    jsondata = json.loads(open(annotsynapsefile, 'rt').read())
    metadata = jsondata["metadata"]
    if metadata["description"] != "synapse annotations":
        print "not a synpase annotation file!"
        sys.exit(1)
    if metadata["file version"] > 1:
        print "this file is from a newer Raveler than I can handle!"
        sys.exit(1)

    synapse_locations = []
    for synapse in jsondata["data"]:
        tbar_location = synapse["T-bar"]["location"]
        synapse_locations.append(tbar_location)
        for psd in synapse["partners"]:
            psd_location = psd["location"]
            synapse_locations.append(psd_location)

    locs_temp = "syn_locs_" + str(random.randint(0,9999))  + ".json"
    with open(locs_temp, 'wt') as f:
        json.dump(synapse_locations, f, indent=2)

    data = open(locs_temp,'rb').read()
    dvid_request_url= "http://" + dvid_server + "/api/node/" + dvid_uuid + "/" + dvid_roi + "/ptquery";
    print "dvid url " + dvid_request_url
    res = requests.post(url=dvid_request_url,data=data)    
    #print res.text
    roi_query_results = json.loads(res.text)
    
    point_lookup_table = {}
    this_count = 0
    for loc in synapse_locations:
        key = str(loc[0]) + "_" + str(loc[1]) + "_" + str(loc[2])
        in_roi = roi_query_results[this_count]
        #print key + " " + str(in_roi)
        point_lookup_table[key] = in_roi
        this_count+=1

    export_synapses = []

    roi_note = ""
    if roi_toggle:
        roi_note = "Synapses inside ROI"
        print "Getting synapses in roi"
    else:
        roi_note = "Synapses outside ROI"
        print "Getting synapses outside of roi"

    filtered_tbars = []
    for synapse in jsondata["data"]:
        tbar_data = synapse["T-bar"]
        tbar_loc = tbar_data["location"]
        tbar_key = str(tbar_loc[0]) + "_" + str(tbar_loc[1]) + "_" + str(tbar_loc[2])
        tbar_in_roi = str(point_lookup_table[tbar_key])

        if roi_toggle:
            if tbar_in_roi == "False":
                continue
        else:
            if tbar_in_roi == "True":
                continue        
        print "TBarHere " + tbar_in_roi        
        filtered_psds = []
        for psd in synapse["partners"]:
            psd_loc = psd["location"]
            psd_key = str(psd_loc[0]) + "_" + str(psd_loc[1]) + "_" + str(psd_loc[2])
            psd_in_roi = str(point_lookup_table[psd_key])            
            if roi_toggle:
                if psd_in_roi == "False":
                    continue
            else:
                if psd_in_roi == "True":
                    continue
            print "\tPSDHere " + psd_in_roi
            filtered_psds.append(psd);
        synapse["partners"] = filtered_psds
        filtered_tbars.append(synapse)
        
    print "Done filtering"
    jsondata["data"] = filtered_tbars
    json_meta = jsondata["metadata"]
    json_meta["ROI note"] = roi_note
    json_meta["DVID ROI"] = dvid_roi
    json_meta["DVID uuid"] = dvid_uuid
    json_meta["DVID server"] = dvid_server
    json_meta["software"] = "filter_roi_annot_synapse.py"
    with open(outputfilename, 'wt') as f:
        json.dump(jsondata, f, indent=2)
