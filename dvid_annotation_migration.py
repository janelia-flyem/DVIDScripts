#!/bin/env
"""

migrate one annotations data instance into another data instance.

lau, 01/21 first version of script

example:

"""

# ------------------------- imports -------------------------
import json
import sys
import os
import socket
import datetime
import urllib
import requests
import random

# ------------------------ function to retrieve body ids -------------
def load_dvid_annotations ( formatted_annots, dvid_server, dvid_uuid, annot_data_name, write_count ):
    annotations_temp = "annot_for_dvid_batch_" + str(write_count) + "_" + str(random.randint(0,9999))  + ".json"
    with open(annotations_temp, 'wt') as f:
        json.dump(formatted_annots, f, indent=2)
    dvid_request_url= "http://" + dvid_server + "/api/node/" + dvid_uuid + "/" +  annot_data_name + "/elements"
    print "dvid url " + dvid_request_url
    data = open(annotations_temp,'rb').read()
    res = requests.post(url=dvid_request_url,data=data)
    #don't need these since I don't need the output coming back from dvid
    #thisbodylabeldata = json.loads(res.text)
    #print "this body labels " + str(len(thisbodylabeldata))
    #bodylabeldata.extend(thisbodylabeldata)
    # remove temp json file
    #os.remove(synapses_temp)

# ------------------------- script start -------------------------
if __name__ == '__main__':

    if len(sys.argv) < 8:
        print "usage: dvid_server_exp dvid_node_uuid_exp annot_datatype_exp offsett_coord(x_y_z) size(x_y_z) dvid_server_imp dvid_uuid_imp annot_datatype_imp"
        sys.exit(1)

    dvid_server_exp = sys.argv[1]
    dvid_uuid_exp = sys.argv[2]
    annot_datatype_exp = sys.argv[3]
    offsett_coord = sys.argv[4]
    size = sys.argv[5]
    dvid_server_imp = sys.argv[6]
    dvid_uuid_imp = sys.argv[7]
    annot_datatype_imp = sys.argv[8]

    proxies = {'http': 'http://' + dvid_server_exp + '/'}

    dvid_request_annot_exp = "http://" + dvid_server_exp + "/api/node/" + dvid_uuid_exp + "/" + annot_datatype_exp + "/elements/" + size + "/" + offsett_coord

    print "dvid_url: " + dvid_request_annot_exp

    response = urllib.urlopen(dvid_request_annot_exp, proxies=proxies).read()
    #print "here*" + response + "*"
    if response == 'null':
        print "No elements found in offset " + offsett_coord + " to " + size
        sys.exit(1)
    
    annot_data = json.loads(response)    
    write_count = offsett_coord

    #if len(annot_data) > 0:
    load_dvid_annotations(annot_data, dvid_server_imp, dvid_uuid_imp, annot_datatype_imp, write_count)
    #else:
    #    print "No elements found in offset " + offsett_coord + " to " + size

    sys.exit(1)
