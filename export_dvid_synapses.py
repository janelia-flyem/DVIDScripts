#!/bin/env
"""

export synapses from dvid into annotations synapse json format

lau, 01/16 first version of script

example:
python export_dvid_synapses.py emdata1:8500 3ca7f synapses 1000_3000_4000 5000_5000_2000 export_test.json

note that this script will not detect current body IDs for synapses. Run update_annot_syn_bodyID_batch.py to update the synapse file with most up to date body IDs.

example:
python update_annot_syn_bodyID_batch.py export_test.json export_test_updated.json emdata1:8500 3ca7f labels3 10000

"""

# ------------------------- imports -------------------------
import json
import sys
import os
import socket
import datetime
import urllib
# ------------------------- script start -------------------------
if __name__ == '__main__':

    if len(sys.argv) < 6:
        print "usage: dvid_server dvid_node_uuid synapse_datatype_name offsett_coord(x_y_z) size(x_y_z) outputfilename"
        sys.exit(1)

    dvid_server = sys.argv[1]
    dvid_uuid = sys.argv[2]
    synapse_datatype_name = sys.argv[3]
    offsett_coord = sys.argv[4]
    size = sys.argv[5]
    outputfilename = sys.argv[6]

    proxies = {'http': 'http://' + dvid_server + '/'}

    dvid_request_synapses = "http://" + dvid_server + "/api/node/" + dvid_uuid + "/" + synapse_datatype_name + "/elements/" + size + "/" + offsett_coord
    print "dvid_url: " + dvid_request_synapses
    response = urllib.urlopen(dvid_request_synapses, proxies=proxies).read()
    #print response
    synapsedata = json.loads(response)
    
    export_synapse_tbars = {}
    export_synapses_psds = {}
    for synapse in synapsedata:
        #print "here " + synapse["Kind"] 
        pos = synapse["Pos"]
        
        # deal with presyn
        if synapse["Kind"] == "PreSyn":
            syn_id = str(pos[0]) + "_" + str(pos[1]) + "_" + str(pos[2])
            #print "Tbar: " + syn_id
            export_synapse_tbars[syn_id] = synapse
        # deal with postsyn
        if synapse["Kind"] == "PostSyn":
            # this is an array
            rels = synapse["Rels"]
            presynto = rels[0]
            presyncoord = presynto["To"]
            syn_id = str(presyncoord[0]) + "_" + str(presyncoord[1]) + "_" + str(presyncoord[2])
            #print "\tPSD to: " + syn_id
            check_psd = export_synapses_psds.get(syn_id)
            if check_psd:
                psd_grouped = export_synapses_psds[syn_id]
                psd_grouped.append(synapse)                
            else:
                this_array = []
                this_array.append(synapse)
                export_synapses_psds[syn_id] = this_array
    #

    # Go through all Tbars find PSDS, generate data structure to export to JSON. 
    annot_syn_export = []
    #this_test = export_synapses_psds['Syn28526']
    

    for syn_key in sorted(export_synapse_tbars):
        #print "key " + syn_key
        presyn_data = export_synapse_tbars[syn_key]
        tbar_pos = presyn_data['Pos']
        tbar_properties = presyn_data['Prop']
        tbar_confidence = 1
        if ('confidence' in tbar_properties):
            tbar_confidence = tbar_properties['conf']
        tbar_user = "";
        if ('agent' in tbar_properties):
            tbar_user = tbar_properties['agent']
        if ('user' in tbar_properties):
            tbar_user = tbar_properties['user']
        #print "x " + str(tbar_pos[0])
        this_synapse_data = {}
        
        this_tbar_data = {}
        this_tbar_data["status"] = "final"
        this_tbar_data["user"] = tbar_user
        this_tbar_data['confidence'] = float(tbar_confidence)
        this_tbar_data['body ID'] = -1
        this_tbar_data['location'] = tbar_pos
        if ('multi' in tbar_properties):
            this_tbar_data['multi'] = "multi"
        if ('convergent' in tbar_properties):
            this_tbar_data['convergent'] = "convergent"
        if ('flagged' in tbar_properties):
            flagged = 0
            if tbar_properties['flagged'] == "True":
                flagged = 1
            else:
                flagged= 0
            this_tbar_data['flagged'] = bool(flagged)
        check_for_psds = export_synapses_psds.get(syn_key)
        psd_partners = []
        if check_for_psds:
            postsyn_array = export_synapses_psds[syn_key]
            for postsyn_data in postsyn_array:
                psd_properties = postsyn_data['Prop']
                psd_confidence = 1
                if ('confidence' in psd_properties):
                    psd_confidence = psd_properties['conf']
                psd_user = "";
                if ('agent' in psd_properties):
                    psd_user = psd_properties['agent']
                if ('user' in psd_properties):
                    psd_user = psd_properties['user']
                psd_location = postsyn_data['Pos']
                psd_export = {}
                psd_export['body ID'] = -1
                psd_export['user'] = psd_user
                psd_export['confidence'] = float(psd_confidence)
                psd_export['traced'] = bool("False")
                psd_export['location'] = psd_location
                if ('flagged' in psd_properties):
                    pflagged = 0
                    if psd_properties['flagged'] == "True":
                        pflagged = 1
                    else:
                        pflagged = 0
                    psd_export['flagged'] = bool(pflagged)
                psd_partners.append(psd_export)
        else:
            print "warning: could not find psds for synapse " + syn_key        
        this_synapse_data["T-bar"] = this_tbar_data
        this_synapse_data["partners"] = psd_partners
        annot_syn_export.append(this_synapse_data);

    # export json
    annot_syn_metadata = {}
    annot_syn_metadata['username'] = "flyem"
    annot_syn_metadata['description'] = "synapse annotations"
    annot_syn_metadata['coordinate system'] = "dvid"
    annot_syn_metadata['software'] = "export_dvid_synapses.py"
    annot_syn_metadata['software version'] = "1.0.0"
    annot_syn_metadata['file version'] = 1
    annot_syn_metadata['session path'] = os.getcwd()
    annot_syn_metadata['computer'] = socket.gethostname()
    annot_syn_metadata['date'] = datetime.datetime.now().strftime("%d-%B-%Y %H:%M")

    final_json_export = {}
    final_json_export['data'] = annot_syn_export
    final_json_export['metadata'] = annot_syn_metadata

    with open(outputfilename, 'wt') as f:
        json.dump(final_json_export, f, indent=2)
