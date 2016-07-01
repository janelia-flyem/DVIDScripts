#!/bin/env
"""

export body synapses from dvid into annotations synapse json format

lau, 01/16 first version of script

example:
python export_body_synapses.py emdata1:8500 3ca7f synapses 32818 export_test.json

"""

# ------------------------- imports -----------------------------
import json
import sys
import os
import socket
import datetime
from libdvid import DVIDNodeService, ConnectionMethod

# ------------------------- functions ---------------------------

# ---- Requires dvid labelblk datainstance and 3D coordinates (format of x_y_z), Returns json object with labelID 
def get_dvid_label_id ( node_service, labelblk, coord_string ):
    dvid_request_label = "{0}/label/{1}".format(labelblk,coord_string)
    print "GET LABEL CALL: " + dvid_request_label
    label_response = node_service.custom_request( dvid_request_label, "", ConnectionMethod.GET )
    labeldata = json.loads(label_response)
    return labeldata;

def get_annotated_bodyname ( node_service, bodyannotations, label_id ):
    this_body_name = "Unknown"
    dvid_request_body_annot = "{0}/key/{1}".format(bodyannotations,label_id)
    print "GET ANNOT BODY NAME: " + dvid_request_body_annot
    try:
        bodyannot_response = node_service.custom_request( dvid_request_body_annot, "", ConnectionMethod.GET )
        bodyannotdata = json.loads(bodyannot_response)
        if ('name' in bodyannotdata):
            print bodyannotdata["name"]
            this_body_name = bodyannotdata["name"]
        else:
            this_body_name = "Unknown"
    except:
        print "Warning! label_id: " + str(label_id) + " failed to retrieve a body name from: " + bodyannotations
        this_body_name ="Unknown"
    return this_body_name;

def get_dvid_synapse ( node_service, synapse_datatype_name, synapse_coord):
    dvid_request_get_synapse = "{0}/elements/1_1_1/{1}".format(synapse_datatype_name,synapse_coord)
    print "GET SYNAPSE " + dvid_request_get_synapse
    syn_response = node_service.custom_request( dvid_request_get_synapse, "", ConnectionMethod.GET )
    ar_syn = json.loads(syn_response)
    this_synapse = ar_syn[0]
    return this_synapse;
    
# ------------------------- script start -------------------------
if __name__ == '__main__':

    if len(sys.argv) < 6:
        print "usage: dvid_server dvid_node_uuid synapse_datatype_name labelID outputfilename"
        sys.exit(1)

    dvid_server = sys.argv[1]
    dvid_uuid = sys.argv[2]
    synapse_datatype_name = sys.argv[3]
    label_id = sys.argv[4]
    labelblk = sys.argv[5]
    bodyannotations = sys.argv[6]
    outputfilename = sys.argv[7]

    # Libdvid has problems with trailing slashes in urls
    if dvid_server.endswith('/'):
        dvid_server = dvid_server[0:-1]
    http_dvid_server = "http://{0}".format(dvid_server)
    node_service = DVIDNodeService(dvid_server, dvid_uuid, 'umayaml@janelia.hhmi.org', 'export dvid synapses')
    dvid_request_synapses =  "{0}/label/{1}".format(synapse_datatype_name, label_id)
    #print dvid_request_synapses
    response = node_service.custom_request( dvid_request_synapses, "", ConnectionMethod.GET )

    #print response

    if response == "null":
        print "No synapses found for " + dvid_request_synapses
        sys.exit(1)
        
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
            labeldata = get_dvid_label_id (node_service,labelblk,syn_id)
            print str(labeldata["Label"])
            synapse["Label"] = labeldata["Label"]
            this_body_name = "Unknown"
            this_label_id = labeldata["Label"]
            if this_label_id > 0:
                this_body_name = get_annotated_bodyname(node_service,bodyannotations,this_label_id)
            print "TBAR get name" + this_body_name
            synapse["BodyName"] = this_body_name
            export_synapse_tbars[syn_id] = synapse
            rels = synapse["Rels"]
            if not rels:
                print "Detected no PSDs for PreSyn at " + str(pos[0]) + "_" + str(pos[1]) + "_" + str(pos[2])
                continue
            for r in rels:
                #r["Prop"] = ""
                loc = r["To"]
                psd_coord = str(loc[0]) + "_" + str(loc[1]) + "_" + str(loc[2])
                this_psd = get_dvid_synapse(node_service,synapse_datatype_name,psd_coord)
                labeldata = get_dvid_label_id (node_service,labelblk,psd_coord)
                print str(labeldata["Label"])
                this_psd["Label"] = labeldata["Label"]                
                this_body_name = "Unknown"
                this_label_id = labeldata["Label"]
                if this_label_id > 0:
                    this_body_name = get_annotated_bodyname(node_service,bodyannotations,this_label_id)
                this_psd["BodyName"] = this_body_name
                check_psd = export_synapses_psds.get(syn_id)                
                if check_psd:
                    psd_grouped = export_synapses_psds[syn_id]
                    psd_grouped.append(this_psd)
                else:
                    this_array = []
                    this_array.append(this_psd)
                    export_synapses_psds[syn_id] = this_array


        # deal with postsyn
        if synapse["Kind"] == "PostSyn":
        #    # this is an array            
            psd_coord = str(pos[0]) + "_" + str(pos[1]) + "_" + str(pos[2])
            #print "Tbar: " + syn_id

            labeldata = get_dvid_label_id (node_service,labelblk,psd_coord)
            print str(labeldata["Label"])
            synapse["Label"] = labeldata["Label"]
            this_body_name = "Unknown"
            this_label_id = labeldata["Label"]
            if this_label_id > 0:
                this_body_name = get_annotated_bodyname(node_service,bodyannotations,this_label_id)
            synapse["BodyName"] = this_body_name

            rels = synapse["Rels"]
            if not rels:
                print "Warning detected PSD not associated with Tbar at " + str(pos[0]) + "," + str(pos[1]) + "," + str(pos[2])
                continue
            presynto = rels[0]
            presyncoord = presynto["To"]
            syn_id = str(presyncoord[0]) + "_" + str(presyncoord[1]) + "_" + str(presyncoord[2])
            #print "\tPSD to: " + syn_id
            this_tbar = get_dvid_synapse(node_service,synapse_datatype_name,syn_id)
            labeldata = get_dvid_label_id (node_service,labelblk,syn_id)
            print str(labeldata["Label"])
            this_tbar["Label"] = labeldata["Label"]
            this_body_name = "Unknown"
            this_label_id = labeldata["Label"]
            if this_label_id > 0:
                this_body_name = get_annotated_bodyname(node_service,bodyannotations,this_label_id)
            this_tbar["BodyName"] = this_body_name
            export_synapse_tbars[syn_id] = this_tbar

            check_psd = export_synapses_psds.get(syn_id)
            if check_psd:
                psd_grouped = export_synapses_psds[syn_id]
                psd_grouped.append(synapse)                
            else:
                this_array = []
                this_array.append(synapse)
                export_synapses_psds[syn_id] = this_array



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
        if ('BodyName' in presyn_data):
            this_tbar_data["body name"] = presyn_data["BodyName"]
        else:
            this_tbar_data["body name"] = "Unknown"
        this_tbar_data["status"] = "final"
        this_tbar_data["user"] = tbar_user
        if ('conf' in tbar_properties):
            tbar_confidence = tbar_properties["conf"]
        this_tbar_data['confidence'] = float(tbar_confidence)
        if ('Label' in presyn_data):
            this_tbar_data['body ID'] = presyn_data['Label']
        else:
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
                if ('Prop' in postsyn_data):
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
                if ('Label' in postsyn_data):
                    psd_export['body ID'] = postsyn_data['Label']
                else:
                    psd_export['body ID'] = -1
                psd_export['user'] = psd_user
                if ('BodyName' in postsyn_data):
                    psd_export['body name'] = postsyn_data['BodyName']
                else:
                    psd_export['body name'] = "Unknown"
                if ('conf' in psd_properties):
                    psd_confidence = psd_properties["conf"]
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
            print "warning: could not find psds for synapse " + syn_key + " conf: " + str(tbar_confidence)       
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
