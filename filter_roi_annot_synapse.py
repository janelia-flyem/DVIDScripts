#!/bin/env
"""
Script that will select synapses that are either in a DVID ROI or outside the DVID ROI.

example:
select synapses inside glomerulus roi:
python filter_roi_annot_synapse.py feb24_annot_syn_dvid_ab0efglom_updated.json inside_glom.json emdata1:8500 f94a1 glomerulus 1

select synapses outside of glomerulus roi:
python filter_roi_annot_synapse.py feb24_annot_syn_dvid_ab0efglom_updated.json outside_glom.json emdata1:8500 f94a1 glomerulus 0

lau, 2/16

"""

# ------------------------- imports -------------------------
import json
import urllib2
import copy
import os
import argparse
from libdvid import DVIDNodeService, ConnectionMethod, DVIDConnection
from libdvid._dvid_python import DVIDException
# ------------------------- fuctions -------------------------

def getAnnotations(nodeservice, dataname, size, offsets):
	'''
	Gets the annotations for a substack
	Args: nodeservice, the dvid dataname, size tuple, offsets tuple
	Returns: json parsed result (list of dictionaries in this case)
	'''
	endpoint = "{}/elements/{}_{}_{}/{}_{}_{}".format(dataname, size[0], size[1], size[2], offsets[0], offsets[1], offsets[2])
	result = nodeservice.custom_request(endpoint, None, ConnectionMethod.GET)
	return json.loads(result)

def getGrayscaleBounds(nodeservice, grayscale='grayscale'):
	endpoint = "{}/info".format(grayscale)
	result = nodeservice.custom_request(endpoint, None, ConnectionMethod.GET)
	data = json.loads(result)
	return {
		"offset": data['Extended']['MinPoint'],
		"size": [data['Extended']['MaxPoint'][0] + data['Extended']['MinPoint'][0],
			data['Extended']['MaxPoint'][1] + data['Extended']['MinPoint'][1],
			data['Extended']['MaxPoint'][2] + data['Extended']['MinPoint'][2]],
	}

def loadBatchSynapses(nodeservice, dataname, synapses):
    data = json.dumps(synapses)
    endpoint = "{}/elements".format(dataname)
    nodeservice.custom_request(endpoint, data, ConnectionMethod.POST)

def createAnnotationDataType(nodeservice, dvidconnection, uuid, dataname):
	# check if datatype exists
	info_endpoint = "{}/info".format(dataname)
	try:
		nodeservice.custom_request(info_endpoint, None, ConnectionMethod.GET)
	except DVIDException as e:
		post_json = json.dumps({
			'typename': 'annotation',
			'dataname': dataname,
			'versioned': '1',
		})
		endpoint = "/repo/{}/instance".format(uuid)
		status, body, error_message = dvidconnection.make_request(endpoint, ConnectionMethod.POST, post_json)


def setUpSyncsForAnnotation(nodeservice, originalAnnotations, destinationAnnotations):
	# get syncs from original annotations
	info_endpoint = "{}/info".format(originalAnnotations)
	result = nodeservice.custom_request(info_endpoint, None, ConnectionMethod.GET)
	info = json.loads(result)
	sync_list = info['Base']['Syncs']
	post_json = json.dumps({
		"sync": ",".join(sync_list),
	})
	sync_endpoint = "{}/sync".format(destinationAnnotations)
	nodeservice.custom_request(sync_endpoint, post_json, ConnectionMethod.POST)


# ------------------------- script start -------------------------
if __name__ == '__main__':

	parser = argparse.ArgumentParser(description="Select synapses that are either in a DVID ROI or outside the DVID ROI")
	parser.add_argument('--server', dest='dvid_server', action='store',help='DVID server name')
	parser.add_argument('--uuid', dest='dvid_uuid', action='store', help='The uuid for DVID')
	parser.add_argument('--roi', dest='dvid_roi', action='store', help='Name for label datastore')
	parser.add_argument('--annotation-datatype', dest='annotdatatype', action='store', default=False, help='Name for annotations datatype')
	parser.add_argument('--output', dest='outputfilename', action='store', help='Output file path')
	parser.add_argument('--batch-count', dest='batch', action='store', default=10000, help="Number of synapses to load at a time so you don't overload DVID")
	parser.add_argument('--no-inside-roi', dest='roi_toggle', action='store_true',  help="Select synapses outside roi")
	args = parser.parse_args()

	annotationsdatatype = args.annotdatatype
	outputfilename = args.outputfilename
	dvid_server = args.dvid_server
	dvid_uuid = args.dvid_uuid
	dvid_roi = args.dvid_roi
	roi_toggle = not args.roi_toggle
	batch = args.batch
	ns = DVIDNodeService(dvid_server, dvid_uuid, 'Lowell Umayam and Charlotte Weaver', 'filter_roi_annot_synapse')
	dc = DVIDConnection(dvid_server, 'Lowell Umayam and Charlotte Weaver', 'filter_roi_annot_synapse')
	# List of synapse locations (both tbars and psds)
	synapse_locations = []

	bounds = getGrayscaleBounds(ns)
	raw_annotations =  getAnnotations(ns, args.annotdatatype, bounds['size'], bounds['offset'])
	for annotation in raw_annotations:
		synapse_locations.append(annotation['Pos'])
		if 'Rel' in annotation:
			for rel in annotation['Rel']:
				synapse_locations.append(rel['To'])

	roi_query_results = ns.roi_ptquery(dvid_roi, synapse_locations)

	point_lookup_table = {}
	for idx, loc in enumerate(synapse_locations):
		key = "{}_{}_{}".format(loc[0], loc[1], loc[2])
		in_roi = roi_query_results[idx]
		point_lookup_table[key] = in_roi

	exported_annotations = []
	for annotation in raw_annotations:
		position = "{}_{}_{}".format(annotation['Pos'][0], annotation['Pos'][1],annotation['Pos'][2])
		if point_lookup_table[position]:
			at_least_one_rel_in_roi = False
			del_idxs = []
			if not annotation['Rels']:
				exported_annotation = copy.deepcopy(annotation)
				exported_annotations.append(exported_annotation)
			else:
				for idx, rel in enumerate(annotation['Rels']):
					rel_pos = "{}_{}_{}".format(rel['To'][0], rel['To'][1],rel['To'][2])
					if rel_pos not in point_lookup_table or not point_lookup_table[rel_pos]:
						del_idxs.append(idx)
						
					else:
						at_least_one_rel_in_roi = True
				exported_annotation = copy.deepcopy(annotation)
				rels = copy.deepcopy(exported_annotation['Rels'])
				if del_idxs and rels:
					exported_annotation['Rels'] = [i for idx, i in enumerate(rels) if idx not in del_idxs]
				elif rels:
					exported_annotation['Rels'] = rels
				if at_least_one_rel_in_roi:
					exported_annotations.append(exported_annotation)
	# print exported_annotations

	exported_dataname = annotationsdatatype + "_" + dvid_roi
	createAnnotationDataType(ns, dc, dvid_uuid, exported_dataname)
	for i in range(0, len(exported_annotations), batch):
		if i + args.batch > len(exported_annotations):
			batch_synapses = exported_annotations[i:]
		else:
			batch_synapses = exported_annotations[i:i + batch]
		loadBatchSynapses(ns, exported_dataname, batch_synapses)
	setUpSyncsForAnnotation(ns, annotationsdatatype, exported_dataname)
	