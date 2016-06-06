#!/bin/env
"""

migrate one annotations data instance into another data instance.

lau, 01/21 first version of script

example:

"""

# ------------------------- imports -------------------------
import json
import sys
from libdvid import DVIDNodeService, ConnectionMethod

# ------------------------ function to retrieve body ids -------------
def load_dvid_annotations ( formatted_annots, node_service, annot_data_name, write_count ):
    data = json.dumps(formatted_annots)
    dvid_request_url = annot_data_name + "/elements"
    node_service.custom_request(dvid_request_url, data, ConnectionMethod.POST)
    print "dvid url " + dvid_request_url


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

    if dvid_server_exp.endswith('/'):
        dvid_server_exp = dvid_server[0:-1]
    http_dvid_server = "http://{0}".format(dvid_server_exp)
    node_service = DVIDNodeService(http_dvid_server, dvid_uuid_exp, 'umayaml@janelia.hhmi.org', 'dvid annotation migration')
    dvid_request_annot_exp = annot_datatype_exp + "/elements/" + size + "/" + offsett_coord

    response = node_service.custom_request( dvid_request_annot_exp, "", ConnectionMethod.GET )

    if response == 'null':
        print "No elements found in offset " + offsett_coord + " to " + size
        sys.exit(1)

    
    annot_data = json.loads(response)    
    write_count = offsett_coord

    #if len(annot_data) > 0:
    load_dvid_annotations(annot_data, node_service, annot_datatype_imp, write_count)
    #else:
    #    print "No elements found in offset " + offsett_coord + " to " + size

    sys.exit(1)
