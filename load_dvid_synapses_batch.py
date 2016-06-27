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
    user_val - value to populate required user property for synapses. user is the script(if synapses are predicted), individual, group of individuals that created the synapse.
    batch_count - number of synapses to upload to DVID at a time. A value too large could timeout the server request
    synapse_start - number for synapses to start at. Useful if your synapses are seperated across numerous files.

"""

# ------------------------- imports -------------------------
import json
import sys
import urllib
import random
import os
from libdvid import DVIDNodeService, ConnectionMethod

# ------------------------ function to retrieve body ids -------------
def load_dvid_synapses ( formatted_synapses, synapse_data_name, write_count, node_service ):
    data = str(json.dumps(formatted_synapses))
    endpoint = synapse_data_name + "/elements"
    node_service.custom_request(endpoint, data, ConnectionMethod.POST)



# ------------------------- script start -------------------------
if __name__ == '__main__':
    
    if len(sys.argv) < 7:
        print "usage: inputfile dvid_server dvid_node_uuid synapse_datatype_name batch_load_number synapse_num_start"
        sys.exit(1)

    inputfilename = sys.argv[1]
    dvid_server = sys.argv[2]
    dvid_uuid = sys.argv[3]
    synapse_data_name = sys.argv[4]
    user_val = str(sys.argv[5])
    batch_count = int(sys.argv[6])    
    synapse_start = int(sys.argv[7])

   # Libdvid has problems with trailing slashes in urls
    if dvid_server.endswith('/'):
        dvid_server = dvid_server[0:-1]
    http_dvid_server = "http://{0}".format(dvid_server)
    node_service = DVIDNodeService(dvid_server, dvid_uuid, 'flyem@janelia.hhmi.org', 'generate body synapses')
    
    # not much validation here!
    print "opening json"
    jsondata = json.loads(open(inputfilename, 'rt').read())
    print "done reading json"
    print "batch load num " + str(batch_count)

    metadata = jsondata["metadata"]
    if metadata["description"] != "synapse annotations":
        print "not a synpase annotation file!" 
        sys.exit(1)
    if metadata["file version"] > 1:
        print "this file is from a newer Raveler than I can handle!"
        sys.exit(1)

    #proxies = {'http': 'http://' + dvid_server + '/'}
    
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
        tbar_props["user"] = user_val
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
            psd_props["user"] = user_val
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
                load_dvid_synapses(synapses_data,synapse_data_name,write_count,node_service)
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
            load_dvid_synapses(synapses_data,synapse_data_name,write_count,node_service)
            print "request count " + str(write_count)
            syn_count = 0
            synapses_data = []
        print "finished processing: " + synapse_name

    # write out remaining synapses
    write_count += 1
    load_dvid_synapses(synapses_data,synapse_data_name,write_count,node_service)
    syn_count = 0
    synapses_data = []
    sys.exit(1)
# end script
