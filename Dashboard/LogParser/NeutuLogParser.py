import os
import re
import sys
from datetime import datetime, timedelta
import json
import argparse
from pprint import pprint
import neutu_log_module as nt

def findchunks(data):
	"""
	give a list of lines concatenated from multiple log files, find
	the natural chunks, defined as starting with a session load or
	a new day 
	
	note: if someone usually starts the day by opening Raveler and
	loading a session, there will be an uninteresting chunk with
	only the startup messages in it
	
	input: iterable over log lines
	output: iterator that returns lists of lines belonging to one "chunk"
	"""
	chunk = []
	oldline = None
	date_pattern = re.compile("^20[0-9][0-9]-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}")
	node_alias = "Unknown"

	for line in data:
		#strip off loglevel
		l = line[nt.loglevellength:].rstrip()
		#check if line starts with timestamp, if not discard
		if l.startswith('20') and (date_pattern.match(l)):
				chunk.append(line)
		if (len(chunk) > 10000):
			yield chunk
			chunk = []
	if chunk:
		yield chunk

def calctimings(log):
	single_log = {
		'working_time': {},
	}	
	for chunk in findchunks(log):
		start, stop, duration = nt.parsefortime(chunk)
		chunk_time =  nt.getworkingtimeforchunk(chunk)
		chunk_day = start[0:8]
		if chunk_day not in single_log['working_time']:
			single_log['working_time'][chunk_day] = 0
		single_log['working_time'][chunk_day] += chunk_time['working']
	return single_log

def calcactions(log):
	result = {
		"merges": 0,
		"splits": 0,
	}
	for l in log:
		if "Merge operation saved." in l:
			result['merges'] += 1
		if "splitted" in l:
			result['splits'] += 1
		# TODO synapses
		# TODO volume	
		# TODO bodies	
	return result

def parselog(log):
	result = calcactions(log)
	timing = calctimings(log)
	return result, timing

def parsegeneral(logs):
	for log_set in logs:
		fulllog = []
		for logpath in log_set['paths']:
			fulllog.extend(open(logpath).readlines())
		action_log, timing_log = parselog(fulllog)
		results['user'][log_set['user']] = action_log
		results['overall']['merges'] += action_log['merges']
		results['overall']['splits'] += action_log['splits']
	pprint(results)



if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Parse Neutu Logs for Progress Data")
	parser.add_argument('--log_directory', dest='directory', action='store', help='Directory that contains log files')
	parser.add_argument('--output', dest='output_file', action='store', default='neutu.json', help='File Name for output')
	#parser.add_argument('--multiple_datasets', dest='use_multiple_datasets', action='store_true', default=False, help='Flag, separate stats by DVID dataset.\
	# Use this if you have more than one DVID dataset you are using \
	# (but not if you have many nodes for the same dataset)')


	args = parser.parse_args()
	results = {
		'overall': {
			'merges': 0,
			'splits': 0,
		},
		'user': {},
		'timeseries': {},
	}
	# Since we are going to need to chunk the logs differently depending on use, 
	# I'm flattening the generator
	log_locations = [l for l in nt.getloglocations(args.directory)]
	# Parse overall data
	parsegeneral(log_locations)

	# Parse user data

	# Parse timeseries data