# std lib
import datetime
import os
import re
import sys
from datetime import datetime
import json
import argparse


# note that the milliseconds portion is dropped
timestampformat = "%Y-%m-%dT%H:%M:%S.%f"
timestamplength = len("2015-10-13T09:19:36.729")
newtimestampformat = "%Y%m%d %H:%M"
# useful:
secondsperday = 24 * 60 * 60

# idle threshold for working time; default is 10 minutes
defaultworkingthreshold = 10 * 60

# how many idle intervals to report
nidleintervals = 5

# idle threshold for session time; default is 30 minutes
defaultsessionthreshold = 30 * 60

# length of log level statement (INFO, ERROR, etc.)
loglevellength = 6

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

	for line in data:
		#strip off loglevel
		l = line[loglevellength:].rstrip()
		#check if line starts with timestamp, if not discard
		if (date_pattern.match(l)):
			if oldline:
				# when to begin a new chunk?
				if "Start NeuTu - FlyEM" in l: 
					if "Exit NeuTu" in oldline:
						end_type = "close"
					else:
						end_type = "crash"
					yield (end_type, chunk)
					chunk = []
				elif not sameday(oldline, l):
					end_type = "new_day"
					yield (end_type, chunk)
					chunk = []				
			oldline = l
			chunk.append(line)
	end_type = "working"
	yield (end_type, chunk)


def gettimestamp(line):
	timestamp = line[0:timestamplength]

	return datetime.strptime(timestamp, timestampformat)

def sameday(oldline, line):
	oldtime = gettimestamp(oldline)
	newtime = gettimestamp(line)
	if oldtime.day != newtime.day:
		return False
	else:
		return True

def parsechunk(chunk):
	starttime = gettimestamp(chunk[0][loglevellength:])
	endtime = gettimestamp(chunk[-1][loglevellength:])
	duration = (endtime-starttime).total_seconds()
	starttime = starttime.strftime(newtimestampformat)
	endtime = endtime.strftime(newtimestampformat)
	return starttime, endtime, duration

def parselog(log, single_log):
	for ctype, chunk in findchunks(log):
		start, stop, duration = parsechunk(chunk)
		single_log['start'].append(start)
		single_log['stop'].append({
				'time': stop,
				'type': ctype,
			})
		single_log['duration'].append(duration)
		chunk_time =  getworkingtimeforchunk(chunk)
		chunk_day = start[0:8]
		if chunk_day not in single_log['session_time']:
			single_log['session_time'][chunk_day] = 0
		single_log['session_time'][chunk_day] += chunk_time['session']
		if chunk_day not in single_log['working_time']:
			single_log['working_time'][chunk_day] = 0
		single_log['working_time'][chunk_day] += chunk_time['working']
	return single_log


def parsealllogs(log_locations):
	result = {}
	for logset in log_locations:
		single_log = {
			'start': [],
			'stop': [],
			'duration': [],
			'session_time': {},
			'working_time': {}
		}	
                fulllog = []
		for logpath in logset['paths']:
			fulllog.extend(open(logpath).readlines())
		single_log = parselog(fulllog, single_log)
		result[logset['user']] = single_log
	return result


def get_log_locations(directory):
	# Could yield instead if only going through logs once
	for w in os.walk(directory):
		if 'log.txt' in w[2]:
			username = os.path.basename(w[0])
			yield {
				'user': username,
				'paths': [os.path.join(w[0], fn) for fn in sortloglist(w[2]) ]
			}

def getintervals(timestamps):
	"""
	input: list of timestamps
	output: list of intervals
	"""
	return [t2-t1 for t1, t2 in runningpairs(timestamps)]	

def getworkingtimeforchunk(data):
	"""
	given a list of data lines, return two lists of t1, dt corresponding
	to working and idle times
	
	input: data
	output: two lists of (t1, dt) intervals, working and idle
	"""
	
	timestamps = [gettimestamp(line[loglevellength:]) for line in data]
	intervals = getintervals(timestamps)
	working = []
	session = []
	for dt in intervals:
		if dt.total_seconds() < defaultworkingthreshold:
			working.append(dt.total_seconds())
		if dt.total_seconds() < defaultsessionthreshold:
			session.append(dt.total_seconds())
	return {
		'working': sum(working),
		'session': sum(session) 
	}

def sortloglist(loglist):
	"""
	Sorts the output logs, making oldest first and most recent last.
	
	input: list of log files 
	returns: sorted list of log files in chronological order
	"""
	currentlogfilename = 'log.txt'
	# Remove the current file and reinsert it at the end
	loglist.remove(currentlogfilename)
	# Ignore files that aren't logs
	loglist = [ l for l in loglist if currentlogfilename in l]
	# Sort with lowest number log first (format log.txt.1)
	sortedlist = sorted(loglist, key = lambda i: int(i.split('.')[-1]))
	sortedlist.append(currentlogfilename)
	return sortedlist
	
def runningpairs(sequence):
	"""
	generator for returning successive overlapping pairs from a sequence;
	resulting sequence is N-1 in length if original is length N
	
	eg, runningpairs(range(4)) --> [(0, 1), (1, 2), (2, 3)]
	
	input: iterable
	output: iterator
	"""
	source = iter(sequence)
	last = source.next()
	for next in source:
		yield last, next
		last = next

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Parse Neutu Logs")
	parser.add_argument('--log_directory', dest='directory', action='store', default='/Users/weaverc10/Desktop/neutulogs/neutu_log/', help='Directory that contains log files')
	parser.add_argument('--output', dest='output_file', action='store', default='neutu_start_stop.json', help='File Name for output')
	args = parser.parse_args()
	log_locations = get_log_locations(args.directory)
	result = parsealllogs(log_locations)

	with open(args.output_file, 'w') as output:
		json.dump(result, output)
