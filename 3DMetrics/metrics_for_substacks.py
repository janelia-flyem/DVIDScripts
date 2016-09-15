import json
import time
import argparse
import numpy
from libdvid import DVIDNodeService, ConnectionMethod

def getAnnotations(nodeservice, dataname, size, offsets):
	'''
	Gets the annotations for a substack
	Args: nodeservice, the dvid dataname, size tuple, offsets tuple
	Returns: json parsed result (list of dictionaries in this case)
	'''
	endpoint = "{}/elements/{}_{}_{}/{}_{}_{}".format(dataname, size[0], size[1], size[2], offsets[0], offsets[1], offsets[2])
	result = nodeservice.custom_request(endpoint, None, ConnectionMethod.GET)
	return json.loads(result)

def getROIPartition(nodeservice, dataname, size):
	endpoint = "{}/partition?batchsize={}".format(dataname, size)
	result = nodeservice.custom_request(endpoint, None, ConnectionMethod.GET)
	result = json.loads(result)
	substacks = []
	for substack in result['Subvolumes']:
		substacks.append({
			'x': int(substack['MinPoint'][0]),
			'y': int(substack['MinPoint'][1]),
			'z': int(substack['MinPoint'][2]),
			'percent': float(substack['ActiveBlocks'])/ float(substack['TotalBlocks']),
			'total': float(substack['TotalBlocks']),
			'active': float(substack['ActiveBlocks'])
			})
	return substacks

def makeSubstacksTable(substacks, metric='annotation', filename=None):
	import csv
	if not filename:
		filename = 'substacks_table.xls'
	with open(filename, 'wb') as fh:
		c_writer = csv.writer(fh, delimiter='\t')
		headers = ["id", "x", "y", "z", "width", "length", "height", metric, "percentage active blocks"]
		c_writer.writerow(headers)
		for substack in substacks:
			row = [substack['id'], substack['x'], substack['y'], substack['z'], substack['width'],
				substack['length'], substack['height'], substack['annotations'], substack['percentage']]
			c_writer.writerow(row)

def makeAllSubstacksTable(substacks, filename=None):
	import csv
	if not filename:
		filename = 'substacks_table.xls'
	header = ["id", "x", "y", "z", "width", "length", "height"]
	metrics = set(substacks[0].keys())
	metrics = list(metrics.difference(set(header)))
	header.extend(metrics)

	with open(filename, 'wb') as fh:
		c_writer = csv.writer(fh, delimiter='\t')
		c_writer.writerow(header)
		for substack in substacks:
			row = []
			for key in header:
				row.append(substack[key])
			c_writer.writerow(row)

def isSynapseInBody(nodeservice, dataname, synapse, bodylist):
	inBody = True
	count = 0
	position = synapse['Pos']
	position.reverse()
	label = int(nodeservice.get_label_by_location(dataname, position))
	if label in bodylist:
		for rel in synapse['Rels']:
			if rel['Rel'] == 'PreSynTo':
				relpostion = rel['To']
				relpostion.reverse()
				label = int(nodeservice.get_label_by_location(dataname, relpostion))
				if label in bodylist:
					count += 1
	else:
		inBody = False
	return inBody, count

def make3DJSON(metrics, annotation_keys, roi_name):
	for k in annotation_keys:
		json_out = []
		for substack in metrics:
			new_substack = dict(substack)
			new_substack['annotations'] = new_substack[k]
			new_substack['status'] = new_substack[k]
			json_out.append(new_substack)
		snake_case_annotation = k.replace(' ', '_').replace('/', '_')
		with open("{}_{}.json".format(roi_name, snake_case_annotation), 'w') as out:
			out.write(json.dumps(json_out, indent=4))



if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Extract sizes of all bodies in an ROI.")
	parser.add_argument('--server', dest='server', action='store',	default='emdata2:8000', help='DVID server name')
	parser.add_argument('--uuid', dest='uuid', action='store', default='dd02', help='The uuid for DVID')
	parser.add_argument('--label', dest='labelname', action='store', default='segmentation', help='Name for label datastore')
	parser.add_argument('--body', dest='bodyname', action='store', help='Name for body keyvalue datastore')
	parser.add_argument('--bodypath', dest='bodypath', action='store', help='file with list of bodies')
	parser.add_argument('--input', dest='inputjson', action='store', help='input json (instead of building from DVID)')
	parser.add_argument('--annotation', dest='annotationname', action='store',
	 default='combined_synapses_08302016', help='Name for annotation datastore')
	parser.add_argument('--partition', dest='PARTITION_SIZE', action='store', default=16,
	 type=int, help='Partition size (number of blocks in one dimension)')
	parser.add_argument('--roi', dest='roi', action='store',
	 default='roi_rough_PB26', help='ROI name')
	args = parser.parse_args()
	ns = DVIDNodeService(args.server, args.uuid, 'Charlotte Weaver', 'annotations per volume')
	BLOCK_SIZE = 32
	SUBSTACK_LENGTH = BLOCK_SIZE * args.PARTITION_SIZE

	if args.inputjson:
		with open(args.inputjson) as fh:
			metrics = json.load(fh)
			makeAllSubstacksTable(metrics, "{}_substack_metrics.xls".format(args.roi))
			make3DJSON(metrics, ["edges", "unassigned edges", "assigned edges", "tbars/active volume", "psds/active volume", "tbars/total volume", "psds/total volume", "percent assigned edges"], args.roi)
		print "Completed writing output"
		exit()

	#substacks, packing_factor = ns.get_roi_partition(args.roi, args.PARTITION_SIZE)
	substacks =  getROIPartition(ns, args.roi, args.PARTITION_SIZE)
	bodysizes = {}
	if args.bodyname:
		bodylist = ns.get_keys(args.bodyname)
		bodylist = [int(body) for body in bodylist]
	elif args.bodypath:
		bodylist = []
		with open(args.bodypath) as fh:
			for line in fh:
				bodyid = line.split('\t')[0]
				bodylist.append(int(bodyid))

	print "Substack count: {}".format(len(substacks))
	substack_metrics = []
	for iter1, substack in enumerate(substacks):
		# XYZ coordinates
		z, y, x = substack['z'], substack['y'], substack['x']
		zsize, ysize, xsize = SUBSTACK_LENGTH, SUBSTACK_LENGTH, SUBSTACK_LENGTH
		# TODO make annotations a dictionary for each metric, and then display on graph
		substack_dict = {
			"id": "{}-{}".format(args.roi, iter1),
			"x" : x,
			"y" : y,
			"z" : z,
			"width" : xsize,
			"length" : ysize,
			"height" : zsize,
			"tbars": 0,
			"psds": 0,
			"edges": 0,
			"assigned edges": 0,
			"unassigned edges": 0,
			"tbars/active volume": 0,
			"psds/active volume": 0,
			"tbars/total volume": 0,
			"psds/total volume": 0,
			"percent assigned edges": 0,
			"total volume": 0,
			"active volume": 0,
			"body list": [],
			"percentage active volume": 0,
			"annotations": "",
		}
		print "Percentage active: {}".format(substack['percent'])
		annotations = getAnnotations(ns, args.annotationname, (xsize, ysize, zsize), (x, y, z))
		substack_dict['percentage active volume'] = substack['percent']
		substack_dict['total volume'] = substack['total']
		substack_dict['active volume'] = substack['active']

		if annotations is not None:
			for annotation in annotations:
				if annotation['Kind'] == 'PreSyn':
					substack_dict['tbars'] += 1
					isInBody, count = isSynapseInBody(ns, args.labelname, annotation, bodylist)
					if isInBody:
						substack_dict['assigned edges'] += count
					substack_dict['edges'] += len([a for a in annotation['Rels'] if a['Rel'] == 'PreSynTo'])
				elif annotation['Kind'] == 'PostSyn':
					substack_dict['psds'] += 1
			active_volume = float(substack_dict['active volume']) or 1.0
			substack_dict['tbars/active volume'] = substack_dict['tbars'] / active_volume
			substack_dict['psds/active volume'] = substack_dict['psds'] / active_volume
			substack_dict['tbars/total volume'] = float(substack_dict['tbars']) / float(substack_dict['total volume'])
			substack_dict['psds/total volume'] = float(substack_dict['psds']) / float(substack_dict['total volume'])
			substack_dict['unassigned edges'] = substack_dict['edges'] - substack_dict['assigned edges']
			if substack_dict['edges']:
				substack_dict['percent assigned edges'] = float(substack_dict['assigned edges'])/float(substack_dict['edges'])
		substack_metrics.append(substack_dict)

	with open('{}_all_metircs.json'.format(args.roi), 'wb') as fh:
		fh.write(json.dumps(substack_metrics, indent=4))

	makeAllSubstacksTable(substack_metrics, "{}_substack_metrics.xls".format(args.roi))
	make3DJSON(substack_metrics, ["edges", "assigned edges", "unassigned edges", "tbars/active volume", "psds/active volume", "tbars/total volume", "psds/total volume", "percent assigned edges"], args.roi)
	# Write output
	# makeSubstacksTable(substack_metrics, "{}_substack_metrics.xls".format(args.roi))
	# make3DJSON(substack_metrics, ["tbars/active volume", "psds/active volume", "tbars/total volume", "psds/total volume", "percent assigned edges"], args.roi)
	# # makeSubstacksTable(substacks_tbars, 'tbars per active volume', "{}_tbars.xls".format(args.roi))
	# # makeSubstacksTable(substacks_psds, 'psds per active volume', "{}_psds.xls".format(args.roi))
	# # makeSubstacksTable(substacks_edge_coverage, 'edges per active volume', "{}_edges.xls".format(args.roi))
	# # tbaroutfile = "{}_tbars_unit.json".format(args.roi)
	# psdoutfile = "{}_psds.json".format(args.roi)
	# edgeoutfile = "{}_edges.json".format(args.roi)
	# with open(tbaroutfile, 'w') as out:
	# 	out.write(json.dumps(substacks_tbars, indent=4))
	# with open(psdoutfile, 'w') as out:
	# 	out.write(json.dumps(substacks_psds, indent=4))
	# with open(edgeoutfile, 'w') as out:
	# 	out.write(json.dumps(substacks_edge_coverage, indent=4))
