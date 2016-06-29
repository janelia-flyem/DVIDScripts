#!/bin/env
"""

export annotation datatype from dvid into annotations bookmark json format

lau, 01/16 first version of script

example:
python /groups/flyem/home/flyem/bin/python/dvid_bookmarks/export_dvid_bookmarks.py emdata2:7000 d5053 bookmark_annotations user:takemuras annotations-bookmarks_test.json

"""

# ------------------------- imports -------------------------
import json
import sys
import os
import socket
import datetime
from libdvid import DVIDNodeService, ConnectionMethod
# ------------------------- script start -------------------------
if __name__ == '__main__':

    if len(sys.argv) != 6:
        print "usage: dvid_server dvid_node_uuid synapse_datatype_name tagname outputfilename"
        sys.exit(1)

    dvid_server = sys.argv[1]
    dvid_uuid = sys.argv[2]
    datatype_name = sys.argv[3]
    tag_name = sys.argv[4]
    outputfilename = sys.argv[5]

    if dvid_server.endswith('/'):
        dvid_server = dvid_server[0:-1]
    http_dvid_server = "http://{0}".format(dvid_server)    
    node_service = DVIDNodeService(dvid_server, dvid_uuid, 'umayaml@janelia.hhmi.org', 'export bookmarks')

    tag_endpoint = "{0}/tag/{1}".format(datatype_name, tag_name)
    response = node_service.custom_request( tag_endpoint, '', ConnectionMethod.GET )

    #print response
    bookmarkdata = json.loads(response)

    if not bookmarkdata:
	print "Error, no data for label: {0}".format(tag_name)
	exit(1)
    
    export_bookmarks = []
    
    for bookmark in bookmarkdata:
        #print "here " + synapse["Kind"] 
        pos = bookmark["Pos"]
        props = bookmark["Prop"]
        kind  = bookmark["Kind"]
        tags = bookmark["Tags"]
        bodyID = props["body ID"]

        this_bkm_data = {}
        this_bkm_data["location"] = pos
        this_bkm_data["body ID"] = int(bodyID)
        if "comment" in props:
            comment = props["comment"]
            this_bkm_data["comment"] = comment
        this_bkm_data["text"] = tags[0]
        this_bkm_data["checked"] = True
        this_bkm_data["custom"] = True
        export_bookmarks.append(this_bkm_data)


    # export json
    annot_syn_metadata = {}
    annot_syn_metadata['username'] = "flyem"
    annot_syn_metadata['description'] = "bookmarks"
    annot_syn_metadata['coordinate system'] = "dvid"
    annot_syn_metadata['software'] = "export_dvid_bookmarks.py"
    annot_syn_metadata['software version'] = "1.0.0"
    annot_syn_metadata['file version'] = 1
    annot_syn_metadata['session path'] = os.getcwd()
    annot_syn_metadata['computer'] = socket.gethostname()
    annot_syn_metadata['date'] = datetime.datetime.now().strftime("%d-%B-%Y %H:%M")

    final_json_export = {}
    final_json_export['data'] = export_bookmarks
    final_json_export['metadata'] = annot_syn_metadata

    with open(outputfilename, 'wt') as f:
        json.dump(final_json_export, f, indent=2)
