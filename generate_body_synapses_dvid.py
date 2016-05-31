#!/bin/env
"""

Script that generates body_synapse file using specified annotation datatype with synapes.

lau, 01/16 first version of script

example:
python generate_body_synapses_dvid.py emdata1:8500 44d42 bodies3_annotations mb6_synapses annotations body_synapses_test


"""

# ------------------------- imports -------------------------
import json
import sys
import os
import socket
import datetime
import urllib
import random
import requests
from libdvid import DVIDNodeService, ConnectionMethod

# ------------------------ function to load/post body_synapse to DVID  -------------
def load_body_synpase_dvid (body_synapses, keyvalue_name, key_name, node_service):
    body_synapse_json = "body_synapse_tmp_" + str(random.randint(0,9999))  + ".json" 
    with open(body_synapse_json, 'wt') as f:
        json.dump(body_synapses, f, indent=2)
    data = open(body_synapse_json,'rb').read()
    dvid_request_url = keyvalue_name + "/key/" + key_name
    # print "dvid post url: " + dvid_request_url
    # data = json.dumps(body_synapses)
    # print type(data)
    # print type(body_synapses)
    node_service.put(body_synapses, key_name, data)
    print "Done posting"
    os.remove(body_synapse_json)


# ------------------------- script start -------------------------
if __name__ == '__main__':

    if len(sys.argv) < 6:
        print "usage: dvid_server dvid_node_uuid body_annotations_name(keyvalue) annotations_synapses(annotations) annotations_keyvalue(keyvalue) body_synapses_key(key)"
        print "ex: python ./generate_body_synapses_dvid.py emdata1:8500 44d42 bodies3_annotations mb6_synapses annotations body_synapses_test"
        sys.exit(1)

    dvid_server = sys.argv[1]
    dvid_uuid = sys.argv[2]
    body_annotations_name = sys.argv[3]
    annotations_synapses = sys.argv[4]
    annotations_keyvalue = sys.argv[5]
    body_synapses_key = sys.argv[6]

    # Libdvid has problems with trailing slashes in urls
    if dvid_server.endswith('/'):
        dvid_server = dvid_server[0:-1]
    http_dvid_server = "http://{0}".format(dvid_server)    
    node_service = DVIDNodeService(dvid_server, dvid_uuid, 'umayaml@janelia.hhmi.org', 'generate body synapses')
    response = node_service.get_keys(body_annotations_name)


    # proxies = {'http': 'http://' + dvid_server + '/'}

    # dvid_get_annotated_bodies = "http://" + dvid_server + "/api/node/" + dvid_uuid + "/" + body_annotations_name + "/keys"

    # print "dvid_url " + dvid_get_annotated_bodies

    # response = urllib.urlopen(dvid_get_annotated_bodies, proxies=proxies).read()


    bodies_annot_data = list(response)

    group_synapses = []
    body_theshold = 0
    for key in bodies_annot_data:
        if key.isdigit():
            #print "key " + key
            # key is a bodyID
            # get synapses for bodyID like this http://emdata1.int.janelia.org:8500/api/node/44d42/mb6_synapses/label/10095139
            get_synapses_dvid = annotations_synapses + "/label/" + key
            response_syn = node_service.custom_request( get_synapses_dvid, "", ConnectionMethod.GET )
            # get_synapses_dvid = "http://" + dvid_server + "/api/node/" + dvid_uuid + "/" + annotations_synapses + "/label/" + key
            # print "get syn: " + get_synapses_dvid
            # response_syn = urllib.urlopen(get_synapses_dvid, proxies=proxies).read()
            if response_syn == 'null':
                print "No synapse data found for bodyID: " + key
            else:
                print "Found synapse data for bodyID: " + key
                body_synapses = {}
                #get_body_annot = "http://" + dvid_server + "/api/node/" + dvid_uuid + "/" + body_annotations_name + "/key/"+ key
                #response_bod_annot = urllib.urlopen(get_body_annot, proxies=proxies).read()
                #body_annot_data = json.loads(response_bod_annot)
                #print body_annot_data
                synapse_data = json.loads(response_syn)
                body_theshold += 1                
                syn_count = 0
                psd_count = 0
                tbar_count = 0
                all_locations = {}
                z_locs = []
                for synapse in synapse_data:
                    syn_count += 1
                    syn_kind = synapse['Kind']
                    if syn_kind == 'PreSyn':
                        tbar_count += 1
                    if syn_kind == 'PostSyn':
                        psd_count += 1
                    syn_pos = synapse['Pos']
                    syn_z = syn_pos[2]
                    all_locations[syn_z] = syn_pos
                    z_locs.append(syn_z)
                z_locs.sort()
                loc_num = len(z_locs);
                mid = int(loc_num/2)
                if mid != 0:
                    z_key = z_locs[mid]                
                    #print "Here " + key + " " + str(syn_count) + " " + str(tbar_count) + " " + str(psd_count) + " locnum " + str(loc_num) + " mid " + str(mid) + " zkey " + str(z_key)
                    this_loc = all_locations[z_key]
                    export_synapse_data = {}
                    export_synapse_data["body ID"] = int(key)
                    export_synapse_data["body synapses"] = syn_count
                    export_synapse_data["body PSDs"] = psd_count
                    export_synapse_data["body T-bars"] = tbar_count
                    export_synapse_data["location"] = this_loc
                    text_val = "orphan-link assignment. " + str(syn_count) + " Synapses, " + str(tbar_count) + " T-bars, " + str(psd_count) + " PSDs"                
                    export_synapse_data["text"] = text_val
                    export_synapse_data["body threshold"] = body_theshold
                    group_synapses.append(export_synapse_data)

    print "Done going through bodyIDs"
    syn_body_metadata = {}
    syn_body_metadata['username'] = "flyem"
    syn_body_metadata['description'] = "bookmarks"
    syn_body_metadata['coordinate system'] = "dvid"
    syn_body_metadata['software'] = "generate_body_synapses_dvid.py"
    syn_body_metadata['software version'] = "1.0.0"
    syn_body_metadata['file version'] = 1
    syn_body_metadata['session path'] = os.getcwd()
    syn_body_metadata['computer'] = socket.gethostname()
    syn_body_metadata['date'] = datetime.datetime.now().strftime("%d-%B-%Y %H:%M")

    final_json_export = {}
    final_json_export['data'] = group_synapses
    final_json_export['metadata'] = syn_body_metadata

    load_body_synpase_dvid (final_json_export, annotations_keyvalue, body_synapses_key, node_service)
    sys.exit(1)
