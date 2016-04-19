#!/bin/env
"""

update_annot_syn_bodyID_batch.py

script that will update an annotations synapse json file with new bodies ids retrieved from DVID.

"""

# ------------------------- imports -------------------------
import json
import sys
import requests
import urllib
import random
import os

# ------------------------ function to retrieve body ids -------------
def get_dvid_body_ids( synapse_locations, dvid_server, bodylabeldata, write_count ):
    coords_temp = "coords_for_dvid_batch_" + str(write_count) + "_" + str(random.randint(0,9999))  + ".json"
    with open(coords_temp, 'wt') as f:
        json.dump(synapse_locations, f, indent=2)
    dvid_request_url= "http://" + dvid_server + "/api/node/" + dvid_uuid + "/" +  labelblk + "/labels"
    print "dvid url " + dvid_request_url    
    data = open(coords_temp,'rb').read()
    res = requests.get(url=dvid_request_url,data=data)
    thisbodylabeldata = json.loads(res.text)
    #print "this body labels " + str(len(thisbodylabeldata))
    bodylabeldata.extend(thisbodylabeldata)
    os.remove(coords_temp)
    #return thisbodylabeldata

# ------------------------- script start -------------------------
if __name__ == '__main__':
    
    if len(sys.argv) < 6:
        print "usage: inputfile outputfile dvid_server dvid_node_uuid labelbk_name batch_request_number"
        sys.exit(1)

    inputfilename = sys.argv[1]
    outputfilename = sys.argv[2]
    dvid_server = sys.argv[3]
    dvid_uuid = sys.argv[4]
    labelblk = sys.argv[5]
    batch_count = int(sys.argv[6])

    print "opening json"
    jsondata = json.loads(open(inputfilename, 'rt').read())
    print "done reading json"
    print "batch num " + str(batch_count)

    metadata = jsondata["metadata"]
    if metadata["description"] != "synapse annotations":
        print "not a synpase annotation file!" 
        sys.exit(1)
    if metadata["file version"] > 1:
        print "this file is from a newer Raveler than I can handle!"
        sys.exit(1)

    proxies = {'http': 'http://' + dvid_server + '/'}
    
    synapse_locations = []
    write_count = 0
    syn_count = 0
    bodylabeldata = []
    for synapse in jsondata["data"]:
        tbar_location = synapse["T-bar"]["location"]
        tbar_bodyID = synapse["T-bar"]["body ID"]        
        #print "tbar_x: " + str(tbar_location[0])
        #print "tbar_y: " + str(tbar_location[1])
        #print "tbar_z: " + str(tbar_location[2])
        syn_count +=1
        print "syn count " + str(syn_count)
        synapse_locations.append(tbar_location)
        if (syn_count == batch_count):
            print "syn count T " + str(syn_count)
            write_count += 1
            ret_bodies = get_dvid_body_ids(synapse_locations,dvid_server,bodylabeldata,write_count)
            #print ret_bodies
            print "request count " + str(write_count)
            syn_count = 0           
            synapse_locations = []
            #print "body labels here " + str(len(bodylabeldata))
        for psd in synapse["partners"]:
            psd_location = psd["location"]
            psd_bodyID = psd["body ID"]
            #print "\tpsd_x: " + str(psd_location[0])
            #print "\tpsd_y: " + str(psd_location[1])
            #print "\tpsd_z: " + str(psd_location[2])
            syn_count +=1
            synapse_locations.append(psd_location)
            if (syn_count == batch_count):
                print "syn count P " + str(syn_count)
                write_count += 1
                get_dvid_body_ids(synapse_locations,dvid_server,bodylabeldata,write_count)
                #print "ret body labels a " + str(len(ret_body_ids))
                print "request count " + str(write_count)
                syn_count = 0
                synapse_locations = []
                #print "body labels here" + str(len(bodylabeldata))

    write_count += 1
    get_dvid_body_ids(synapse_locations,dvid_server,bodylabeldata,write_count)
    #bodylabeldata.extend(ret_body_ids)
    syn_count = 0
    synapse_locations = []

    count = 0

    #replace old body ids
    for synapse in jsondata["data"]:
        tbar_location = synapse["T-bar"]["location"]
        tbar_bodyID = synapse["T-bar"]["body ID"]
        print str(count) + " tbar_x: " + str(tbar_location[0])
        print str(count) + " tbar_y: " + str(tbar_location[1])
        print str(count) +" tbar_z: " + str(tbar_location[2])
        synapse_locations.append(tbar_location)
        print "Cur body ID: " + str(tbar_bodyID)
        print "New body ID: " + str(bodylabeldata[count])
        synapse["T-bar"]["body ID"] = bodylabeldata[count]
        #psds_list = synapse["partners"]
        for psd in synapse["partners"]:
            count += 1
            psd_location = psd["location"]
            psd_bodyID = psd["body ID"]
            print "\t" + str(count) + " psd_x: " + str(psd_location[0])
            print "\t" + str(count) + " psd_y: " + str(psd_location[1])
            print "\t" + str(count) + " psd_z: " + str(psd_location[2])
            synapse_locations.append(psd_location)            
            print "\tCur body ID: " +str(psd_bodyID)
            print "\tNew body ID: " +str(bodylabeldata[count])
            psd["body ID"] = bodylabeldata[count]
        count += 1


    #print "this bodyID: " + str(bodylabeldata[0])
    #print "this bodyID: " + str(bodylabeldata[2])

    #write out new annotation synapse json
    with open(outputfilename, 'wt') as f:
        json.dump(jsondata, f, indent=2)


