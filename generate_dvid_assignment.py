#!/bin/env
"""
generate_assignment.py

Light weight assignment generator for tracing bodies in DVID
Generates body centric assignments (body tracing, synapse annotation for a body, etc)
lau, 2/16

"""

# ------------------------- imports -------------------------
import json
import sys
import os
import socket
import datetime
## import urllib
import random
import requests
from libdvid import DVIDNodeService, ConnectionMethod
# ------------------------ function to load/post body_synapse to DVID  -------------
def load_assignment_dvid (json_data, node_service, keyvalue_name, key_name):
    data = json.dumps(json_data)
    node_service.put(keyvalue_name, key_name, data)
    print "Done posting {} : {}".format(keyvalue_name, key_name) 
    #assign_json = "assign_tmp_" + key_name + "_" + str(random.randint(0,9999))  + ".json"
    #with open(assign_json, 'wt') as f:
    #    json.dump(json_data, f, indent=2)
    #dvid_request_url = keyvalue_name + "/key/" + key_name
    #print "dvid post url: " + dvid_request_url
    #data = open(assign_json,'rb').read()
    #res = requests.post(url=dvid_request_url,data=data)
    #print "Done posting " + assign_json 
    #os.remove(assign_json)

# ------------------------- script start -------------------------
if __name__ == '__main__':

    if len(sys.argv) < 8:
        print "usage: python ./generate_bodytrace_assignment.py bodyids.txt emdata2:7000 edaa7 annotations body_synapse_test 9999 emuser body-tracing"
        print "works with both body_synapse and bookmarks in DVID"
        sys.exit(1)

    bodylistfile = sys.argv[1]
    dvid_server = sys.argv[2]
    dvid_uuid = sys.argv[3]
    bodysyn_key_val = sys.argv[4] # key value name where body_synapse or bookmark file is stored
    bodysyn_key = sys.argv[5] # body_synapse file or any bookmark file
    assign_id = sys.argv[6] # provide unique assign_id, either user or some script will generate this, or I can just use random number generator
    user_name = sys.argv[7] # provide username to assign to. Can just submit generic username if wanted
    assign_type = sys.argv[8] # provide assignment type. most likely will all be body tracing assignments, I won't check for some standardize normenclature.
    
    lookup_bodyid = {}
    
    ## Do I comment out proxies?
    #proxies = {'http': 'http://' + dvid_server + '/'}    
    #dvid_get_body_synapse = "http://" + dvid_server + "/api/node/" + dvid_uuid + "/" + bodysyn_key_val + "/key/" + bodysyn_key
    #print "get body synapse " + dvid_get_body_synapse

    if dvid_server.endswith('/'):
        dvid_server = dvid_server[0:-1]
    http_dvid_server = "http://{0}".format(dvid_server)
    node_service = DVIDNodeService(dvid_server, dvid_uuid, 'umayaml@janelia.hhmi.org', 'generate dvid assignment')
    dvid_get_body_synapse = bodysyn_key_val + "/key/" + bodysyn_key 
    
    response = node_service.custom_request( dvid_get_body_synapse, '', ConnectionMethod.GET )

    # need error check here for empty response
    
    body_synapse_data = json.loads(response)
    if type(body_synapse_data) is dict:
        print "Using body synapse format, dict"
        bk_data = body_synapse_data["data"]
    else:
        print "Using bookmark format, list"
        bk_data = body_synapse_data

    # check if it is from body_synapse
    #data_chk = body_synapse_data.get("data")
    #if data_chk:
    #    print "Using body synapse format"
    #    bk_data = body_synapse_data["data"]
    #else:
    #    print "Using bookmark format"
    #    bk_data = body_synapse_data

    for body_syn in bk_data:
        this_bodyid = str(body_syn["body ID"])
        lookup_bodyid[this_bodyid] = body_syn

    assign_bodies = []
    b = open(bodylistfile,'r+')
    for line in b:
        bodyID_chk = line.rstrip('\n')
        print "Check BodyID: " + bodyID_chk
        check_body = lookup_bodyid.get(bodyID_chk)
        if check_body:
            #print "Found " + bodyID_chk
            this_bodyID = check_body["body ID"]
            print "Found BodyID: " + str(this_bodyID)
            assign_data = {}
            assign_data["location"] = check_body["location"]
            assign_data["assignment type"] = assign_type
            assign_data["body ID"] = this_bodyID
            assign_data["custom"] = bool("True")
            assign_data["assign_id"] = int(assign_id)
            assign_bodies.append(assign_data)
        else:
            print "Could Not Find BodyID " + bodyID_chk + " Will Not Assign"


    metadata = {}
    metadata['username'] = "flyem"
    metadata['description'] = "bookmarks"
    metadata['coordinate system'] = "dvid"
    metadata['software'] = "generate_bodytrace_assignment.py"
    metadata['software version'] = "1.0.0"
    metadata['file version'] = 1
    metadata['session path'] = os.getcwd()
    metadata['computer'] = socket.gethostname()
    metadata['date'] = datetime.datetime.now().strftime("%d-%B-%Y %H:%M")

    assign_export = {}
    assign_export["data"] = assign_bodies  
    assign_export["metadata"] = metadata
    
    assign_key_val = "assignments" # better create a dvid keyvalue type called assignments
    assign_key = assign_id + ":" + user_name
    print "Generating Assignment " + assign_key
    load_assignment_dvid(assign_export,dvid_server,dvid_uuid,assign_key_val, assign_key)

    for body_assign in assign_bodies:
        body_id = body_assign['body ID']
        assign_type = body_assign['assignment type']
        assign_id = body_assign['assign_id']
        this_body_assign = {}
        this_body_assign['assign_id'] = assign_id
        this_body_assign['assign_type'] = assign_type
        this_body_assign['body ID'] = body_id
        body_assign_key = "bodyid:" + str(body_id)
        print "Logging Body Assign " + body_assign_key
        load_assignment_dvid(this_body_assign,dvid_server,dvid_uuid,assign_key_val,body_assign_key)

    sys.exit(1)
