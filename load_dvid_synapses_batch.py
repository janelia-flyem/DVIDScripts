#!/bin/env
"""

load synapses into dvid using annotation synapse json files

lau, 12/15

example
python ./load_dvid_synapses_batch.py annotations-synapse_fib25_dvid_e402c_20151222T014833.json emdata2:7000 e402c synapses manual-proof 10000 0
  parameters:
    inputfilename - annotations synapse json file of synapses to load into DVID annotation data type 
    dvid_server - dvid server name
    dvid_uuid - node uuid
    synapse_data_name - annotation data type instance name on dvid server/node
    agent_val - value to populate required agent property for synapses. agent is the script(if synapses are predicted), individual, group of individuals that created the synapse.
    batch_count - number of synapses to upload to DVID at a time. A value too large could timeout the server request
    synapse_start - number for synapses to start at. Useful if your synapses are seperated across numerous files.

"""

# ------------------------- imports -------------------------
import json
import sys
import random
import os
from libdvid import DVIDNodeService, ConnectionMethod

# ------------------------ function to retrieve body ids -------------
def load_dvid_synapses (node_service, formatted_synapses, synapse_data_name):
    dvid_request_url = synapse_data_name + "/elements"
    print "dvid url " + dvid_request_url    
    data = json.loads(formatted_synapses)
    res = requests.post(url=dvid_request_url,data=data)
    node_service.custom_request(dvid_request_url, data, ConnectionMethod.POST)
 


# ------------------------- script start -------------------------
if __name__ == '__main__':
    
    if len(sys.argv) < 7:
        print "usage: inputfile dvid_server dvid_node_uuid synapse_datatype_name batch_load_number synapse_num_start"
        sys.exit(1)

    inputfilename = sys.argv[1]
    dvid_server = sys.argv[2]
    dvid_uuid = sys.argv[3]
    synapse_data_name = sys.argv[4]
    agent_val = str(sys.argv[5])
    batch_count = int(sys.argv[6])    
    synapse_start = int(sys.argv[7])

    #y_adjust = int(sys.argv[3])
    # not much validation here!
    print "opening json"
    jsondata = json.loads(open(inputfilename, 'rt').read())
    print "done reading json"
    print "batch load num " + str(batch_count)

    if dvid_server.endswith('/'):
        dvid_server = dvid_server[0:-1]
    http_dvid_server = "http://{0}".format(dvid_server)    
    node_service = DVIDNodeService(dvid_server, dvid_uuid, 'umayaml@janelia.hhmi.org', 'load dvid synapses')

    metadata = jsondata["metadata"]
    if metadata["description"] != "synapse annotations":
        print "not a synpase annotation file!" 
        sys.exit(1)
    if metadata["file version"] > 1:
        print "this file is from a newer Raveler than I can handle!"
        sys.exit(1)
    
    synapses_data = []
    write_count = 0
    syn_count = 0
    tbar_count = synapse_start
        
    for synapse in jsondata["data"]:
        #tbar_location = synapse["T-bar"]["location"]
        #tbar_bodyID = synapse["T-bar"]["body ID"]
        presyn_rel_type = "PreSynTo"
        tbar_json_data = synapse["T-bar"]
        tbar_location = tbar_json_data["location"]        
        tbar_count +=1
        synapse_name = "Syn" + str(tbar_count);
        presyn_data = {}
        tbar_tags = []
        tbar_props = {}
        tbar_props["agent"] = agent_val
        tbar_tags.append(synapse_name)
        if ('convergent' in tbar_json_data):
            print "T-bar is convergent"
            #presyn_rel_type = "ConvergentTo"
            tbar_props["convergent"] = "True"
            #convergent_tbar_tag = "Convergent"
            #tbar_tags.append(convergent_tbar_tag)
        if ('flagged' in tbar_json_data):
            tbar_props["flagged"] = "True"
            #tbar_flagged = "flagged:flagged"
            #tbar_tags.append(tbar_flagged)
        if ('confidence' in tbar_json_data):
            tbar_props["conf"] = str(tbar_json_data["confidence"])
        if ('multi' in tbar_json_data):
            tbar_props["multi"] = "True"
        presyn_data["Kind"] = "PreSyn"
        presyn_data["Pos"] = tbar_location
        presyn_data["Tags"] = tbar_tags
        presyn_data["Prop"] = tbar_props
        tbars_rels_data = []
        for psd in synapse["partners"]:
            psd_location = psd["location"]
            #psd_bodyID = psd["body ID"]
            postsyn_data = {}
            psd_tags = []
            psd_props = {}
            psd_props["agent"] = agent_val
            #post syn relation to T-bar
            psd_rels_data = []
            post_syn_rel = {}
            post_syn_rel["Rel"] = "PostSynTo"
            post_syn_rel["To"]= tbar_location 
            psd_rels_data.append(post_syn_rel)
            # pre syn relation to PSD
            pre_syn_rel = {}
            #pre_syn_rel["Rel"] = "PreSynTo"
            pre_syn_rel["Rel"] = presyn_rel_type
            pre_syn_rel["To"] = psd_location
            tbars_rels_data.append(pre_syn_rel)            
            # finish with PSD
            psd_tags.append(synapse_name)
            if ('flagged' in psd):
                psd_props["flagged"] = str(psd["flagged"])
                #psd_flagged = "flagged:" + str(psd["flagged"])                
                #psd_tags.append(psd_flagged)
            if ('confidence' in psd):
                psd_props["conf"] = str(psd["confidence"])
            postsyn_data["Kind"] = "PostSyn"
            postsyn_data["Pos"] = psd_location
            postsyn_data["Tags"] = psd_tags
            postsyn_data["Prop"] = psd_props
            postsyn_data["Rels"] = psd_rels_data
            syn_count +=1
            print "syn count " + str(syn_count)
            synapses_data.append(postsyn_data)
            # check to see if it is time to write to dvid
            if (syn_count == batch_count):
                print "syn count P " + str(syn_count) + " eq batch count " + str(batch_count)
                write_count += 1
                load_dvid_synapses(node_service, synapses_data, synapse_data_name)
                print "request count " + str(write_count)
                syn_count = 0
                synapses_data = []
        # end psd loop
        presyn_data["Rels"] = tbars_rels_data
        syn_count +=1
        print "syn count " + str(syn_count)
        synapses_data.append(presyn_data)
        if (syn_count == batch_count):
            print "syn count T " + str(syn_count) +" eq batch count " + str(batch_count)
            write_count += 1
            load_dvid_synapses(node_service, synapses_data, synapse_data_name)
            print "request count " + str(write_count)
            syn_count = 0
            synapses_data = []
        print "finished processing: " + synapse_name

    # write out remaining synapses
    write_count += 1
    load_dvid_synapses(node_service, synapses_data, synapse_data_name)
    #bodylabeldata.extend(ret_body_ids)
    syn_count = 0
    synapses_data = []
    #print "bodys " + str(len(bodylabeldata))
    sys.exit(1)
# end script
