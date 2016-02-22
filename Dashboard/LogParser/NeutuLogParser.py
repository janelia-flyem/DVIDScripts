import os
import re
import sys
from datetime import datetime, timedelta
import json
import argparse
from pprint import pprint
import neutu_log_module as nt


def calctimings(log):
	single_log = {}	
	for end_type, chunk in nt.loadchunks(log):
		start, stop, duration = nt.parsefortime(chunk)
		chunk_time =  nt.getworkingtimeforchunk(chunk)
		chunk_day = start[0:8]
		if chunk_day not in single_log:
			single_log[chunk_day] = {
				'working_time': 0,
				'duration': [],
				'start': [],
				'stop': [],
			}
		single_log[chunk_day]['duration'].append(duration)
		single_log[chunk_day]['start'].append(start)
		single_log[chunk_day]['stop'].append(stop)
		single_log[chunk_day]['working_time'] += chunk_time['working']
	return single_log

def calcactions(log):
	result = {
		"merges": 0,
		"splits": 0,
		"bodies": {},
	}
	day_result = {}
	current_assignment = None
	assignment_chunk = []
	assignment_day_chunk = []
	for l in log:
		if l[nt.loglevellength:].startswith('20'):	
			line_date = nt.gettimestamp(l).strftime(nt.newtimestampformat)[0:8]
			if line_date not in day_result:
				day_result[line_date] = {
					"merges": 0,
					"splits": 0,
					"bodies": {},
				}
				if assignment_day_chunk:
					wt_day = nt.getworkingtimeforchunk(assignment_day_chunk)
					assignment_day_chunk = []
					if current_assignment not in day_result[line_date]['bodies']:
							day_result[line_date]['bodies'][current_assignment] = {
								'merges': 0,
								'splits': 0,
								'working': 0,
							} 
					day_result[line_date]['bodies'][current_assignment]['working'] += wt_day['working']
			if "Assigned bookmark" in l:
				# Retrieve bookmark
				bid = nt.getbookmarkid(l)
				if bid:
					if current_assignment and bid != current_assignment:
						wt = nt.getworkingtimeforchunk(assignment_chunk)
						wt_day = nt.getworkingtimeforchunk(assignment_day_chunk)
						assignment_chunk = []
						assignment_day_chunk = []
						result['bodies'][current_assignment]['working'] += wt['working']
						if current_assignment not in day_result[line_date]['bodies']:
							day_result[line_date]['bodies'][current_assignment] = {
								'merges': 0,
								'splits': 0,
								'working': 0,
							} 
						day_result[line_date]['bodies'][current_assignment]['working'] += wt_day['working']
						# add time to old assignment
					current_assignment = bid
					if current_assignment not in result['bodies']:
						# If not exists, create dictionary
						result['bodies'][current_assignment] = {
							'merges': 0,
							'splits': 0,
							'working': 0,
						}
			if "Merge operation saved." in l:
				result['merges'] += 1
				day_result[line_date]['merges'] += 1
				if current_assignment:
					result['bodies'][current_assignment]['merges'] += 1
					if current_assignment not in day_result[line_date]['bodies']:
						day_result[line_date]['bodies'][current_assignment] = {
							'merges': 0,
							'splits': 0,
							'working': 0,
						}
					day_result[line_date]['bodies'][current_assignment]['merges'] += 1

			if "splitted" in l:
				result['splits'] += 1
				day_result[line_date]['splits'] += 1
				if current_assignment:
					result['bodies'][current_assignment]['splits'] += 1
					if current_assignment not in day_result[line_date]['bodies']:
							day_result[line_date]['bodies'][current_assignment] = {
								'merges': 0,
								'splits': 0,
								'working': 0,
							}
					day_result[line_date]['bodies'][current_assignment]['splits'] += 1
			if current_assignment:
				assignment_chunk.append(l)
				assignment_day_chunk.append(l)
		# TODO synapses
		# TODO volume	
	return result, day_result



def getIntervalData(log):
	'''
	Goes through filelines and gets working intervals
	input: filelines
	output: {"name": [
	{
      "date": "2016-01-05",
      "data": [
        {
          "start": "2016-01-05 12:16",
          "stop": "2016-01-05 12:18",
          "type": "working"
        }
      ]
    },
    {
      "date": "2016-01-08",
      "data": [
        {
          "start": "2016-01-08 15:49",
          "stop": "2016-01-08 15:49",
          "type": "working"
        }
      ]
    }
  ],}
	'''
	data = []
	chunk = []
	old_date = None
	for line in log:
		line_date = nt.gettimestamp(line)
		if not line_date:
			continue
		if not old_date and line_date:
			old_date = line_date.date()
		if old_date and old_date != line_date.date():
			if len(chunk):
				date_string = old_date.strftime('%Y-%m-%d')
				data.append({'date': date_string,'data': nt.getworkingintervalsforchunk(chunk)})
			chunk = []
		chunk.append(line)
		old_date = line_date.date()
	if len(chunk) :
		date_string = old_date.strftime('%Y-%m-%d')
		data.append({'date': date_string,'data': nt.getworkingintervalsforchunk(chunk)})
	return data



def parselog(log):
	result, dailies = calcactions(log)
	timing = calctimings(log)
	return result, dailies, timing

def parsegeneral(logs):
	for log_set in logs:
		fulllog = []
		for logpath in log_set['paths']:
			fulllog.extend(open(logpath).readlines())
		action_log, daily_log, timing_log = parselog(fulllog)
		interval_data = getIntervalData(fulllog)
		results['user'][log_set['user']] = action_log
		results['user'][log_set['user']]['interval'] = interval_data
		results['user'][log_set['user']]['timings'] = timing_log
		results['user'][log_set['user']]['daily'] = daily_log
		for day in daily_log:
			if day not in results['timeseries']['daily']:
				results['timeseries']['daily'][day] = {
					'merges': 0,
					'splits': 0,
				}
			results['timeseries']['daily'][day]['merges'] += daily_log[day]['merges']
			results['timeseries']['daily'][day]['splits'] += daily_log[day]['splits']
		results['overall']['merges'] += action_log['merges']
		results['overall']['splits'] += action_log['splits']
	pprint(results)



if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Parse Neutu Logs for Progress Data")
	parser.add_argument('--log_directory', 
		dest='directory', action='store', help='Directory that contains log files')
	parser.add_argument('--output', 
		dest='output_file', action='store', default='neutu.json', help='Filename for output Default: neutu.json')
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
		'timeseries': {
			'daily': {}
		},
	}
	# Since we are going to need to chunk the logs differently depending on use, 
	# I'm flattening the generator
	log_locations = [l for l in nt.getloglocations(args.directory)]
	# Parse overall data
	parsegeneral(log_locations)


	# Parse timeseries data