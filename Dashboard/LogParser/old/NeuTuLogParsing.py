# std lib
import datetime
import os
import re
import sys
from datetime import datetime, timedelta
import json
import argparse
import urllib2


# note that the milliseconds portion is dropped
timestampformat = "%Y-%m-%dT%H:%M:%S.%f"
timestamplength = len("2015-10-13T09:19:36.729")
newtimestampformat = "%Y%m%d %H:%M"
# useful:
secondsperday = 24 * 60 * 60

# idle threshold for working time; default is 5 minutes
defaultworkingthreshold = 10 * 60

# idle threshold for session time; default is 30 minutes
defaultsessionthreshold = 30 * 60

# length of log level statement (INFO, ERROR, etc.)
loglevellength = 6

db_regex_string = ".*Database ((.*)\:(\d+)\:([A-Fa-f0-9]+)\:(.*)) loaded.*"
db_regex = re.compile(db_regex_string)

# TODO - use libdvid
def getDVIDNodeAlias(server, port, uuid):

	api_url = "http://%s:%s/api/repo/%s/info" % (server, port, uuid)
	try:
		response = urllib2.urlopen(api_url, timeout=10.0)
		info_json = json.load(response)
		return info_json['Alias']
	except urllib2.URLError:
		return "Unknown"

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
		l = line[loglevellength:].rstrip()
		#check if line starts with timestamp, if not discard
		if l.startswith('20') and (date_pattern.match(l)):
			if "Database" in l:
				matches = db_regex.match(l)
				if matches and matches.group(4):
					current_node = matches.group(4)
					current_server = matches.group(2)
					current_port = matches.group(3)
					node_alias = getDVIDNodeAlias(current_server, current_port,current_node)
				if oldline:
					yield(node_alias, chunk)
					chunk = []
				oldline = l
			if oldline:		
				oldline = l
				chunk.append(line)
	if chunk:
		yield (node_alias, chunk)

def parsechunk(chunk):
	try:
		starttime = gettimestamp(chunk[0][loglevellength:])
		endtime = gettimestamp(chunk[-1][loglevellength:])
	except:
		print chunk[0]
		print chunk[1]
		raise
	duration = (endtime-starttime).total_seconds()
	starttime = starttime.strftime(newtimestampformat)
	endtime = endtime.strftime(newtimestampformat)
	return starttime, endtime, duration

def parselog(log):
	results = calcactions(log)
	timings = calctimings(log)
	return results, timings

def calctimings(log):
	single_log = {}	
	for stack, chunk in findchunks(log):
		if stack not in single_log:
			single_log[stack] = {
				'session_time': {},
				'working_time': {},
			}
		start, stop, duration = parsechunk(chunk)
		chunk_time =  getworkingtimeforchunk(chunk)
		chunk_day = start[0:8]
		if chunk_day not in single_log[stack]['session_time']:
			single_log[stack]['session_time'][chunk_day] = 0
		single_log[stack]['session_time'][chunk_day] += chunk_time['session']
		if chunk_day not in single_log[stack]['working_time']:
			single_log[stack]['working_time'][chunk_day] = 0
		single_log[stack]['working_time'][chunk_day] += chunk_time['working']
	return single_log

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

def calcactions(log):
	current_node = None
	current_server = None
	current_port = None
	node_alias = "Unknown"
	time_stamp_start = None
	time_stamp_start_sending = None
	time_stamp_start_dvid = None
	time_stamp_stop_dvid = None

	current_assignment = None
	current_assignment_start_time = None
	assignment_chunk = []
	results = {}
	for l in log:
		if "Database" in l:
			matches = db_regex.match(l)
			if matches and matches.group(4):
				current_node = matches.group(4)
				current_server = matches.group(2)
				current_port = matches.group(3)
				node_alias = getDVIDNodeAlias(current_server, current_port,current_node)
				current_assignment = None
				assignment_chunk = []
		if node_alias != 'Unknown':
			if node_alias not in results:
				results[node_alias] = {
						"merges": 0,
						"splits": 0,
						"split_time": [],
						"split_time_sending": [],
						"split_time_separated": {
                                                        'user': [],     
                                                        'neutu': [],
                                                        'dvid': [],
                                                        'total': [],
                                                },
						"bodies": {},
				}
			if "Assigned bookmark" in l:
				# Retrieve bookmark
				bid = getbookmarkid(l)
				# Set current_assignment
				if bid:
					if bid != current_assignment and current_assignment:
						wt = getworkingtimeforchunk(assignment_chunk)
						assignment_chunk = []
						results[node_alias]['bodies'][current_assignment]['session'] += wt['session'] 
						results[node_alias]['bodies'][current_assignment]['working'] += wt['working'] 
						# add time to old assignment
					current_assignment = bid
					if current_assignment not in results[node_alias]['bodies']:
						# If not exists, create dictionary
						results[node_alias]['bodies'][current_assignment] = {
							'merges': 0,
							'splits': 0,
							'working': 0,
							'session': 0,
						}
				
			if "Merge operation saved." in l:
				results[node_alias]['merges'] += 1
				if current_assignment:
					results[node_alias]['bodies'][current_assignment]['merges'] += 1
			if "Launching split ..." in l:
				time_stamp_start = gettimestamp(l)
			if "Split done. Ready to upload. " in l:
				time_stamp_start_sending = gettimestamp(l)
			if ('extracted' in l) and ('label' in l):
				time_stamp_start_dvid = gettimestamp(l)
			if "Label" in l and "uploaded" in l:
				time_stamp_stop_dvid = gettimestamp(l)
			if "splitted" in l:
				results[node_alias]['splits'] += 1
				if current_assignment:
					results[node_alias]['bodies'][current_assignment]['splits'] += 1
				time_stamp_stop = gettimestamp(l)
				if time_stamp_start:
					time_diff = time_stamp_stop - time_stamp_start
					time_diff_sending = time_stamp_stop - time_stamp_start_sending
					if time_stamp_start_dvid and time_stamp_stop_dvid:
						time_diff_dvid = time_stamp_stop_dvid - time_stamp_start_dvid
					else:
						time_diff_dvid = timedelta()
					time_diff_user = time_diff - time_diff_sending
					time_diff_neutu_processing = time_diff_sending - time_diff_dvid
					results[node_alias]['split_time'].append(time_diff.total_seconds())
					results[node_alias]['split_time_sending'].append(time_diff_sending.total_seconds())
					results[node_alias]['split_time_separated']['user'].append(time_diff_user.total_seconds())
					results[node_alias]['split_time_separated']['neutu'].append(time_diff_neutu_processing.total_seconds())
					results[node_alias]['split_time_separated']['dvid'].append(time_diff_dvid.total_seconds())
					results[node_alias]['split_time_separated']['total'].append(time_diff.total_seconds())
			
			if current_assignment:
				assignment_chunk.append(l)
		else:
			time_stamp_start = None
			time_stamp_start_sending = None
			time_stamp_start_dvid = None
			time_stamp_stop_dvid = None
			current_assginment = None
			assignment_chunk = []
	return results

def getbookmarkid(line):
	bookmarkid = None
	matches = re.search("ID: (\d+) is clicked", line)
	if matches and matches.group(1):
		bookmarkid = matches.group(1)
	return bookmarkid

def gettimestamp(line):
	try:
		timestamp = line[0:timestamplength]
		return datetime.strptime(timestamp, timestampformat)
	except ValueError:
		line = line[loglevellength:]
		timestamp = line[0:timestamplength]
		return datetime.strptime(timestamp, timestampformat)

def parsealllogs(log_locations):
	result = {}
	timing_result = {}
	for logset in log_locations:
		fulllog = []
		for logpath in logset['paths']:
			fulllog.extend(open(logpath).readlines())
		action_log, timing_log = parselog(fulllog)
		result[logset['user']] = action_log
		timing_result[logset['user']] = timing_log
	return result, timing_result


def get_log_locations(directory):
	for w in os.walk(directory):
		if 'log.txt' in w[2]:
			username = os.path.basename(w[0])
			print username
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
	sortedlist.reverse()
	sortedlist.append(currentlogfilename)
	return sortedlist
	
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
	parser.add_argument('--log_directory', dest='directory', action='store', default='/Users/weaverc10/Desktop/neutu_log/', help='Directory that contains log files')
	parser.add_argument('--output', dest='output_file', action='store', default='neutu_actions.json', help='File Name for output')
	parser.add_argument('--timing_output', dest='timing_output_file', action='store', default='neutu_timing.json', help='File Name for timing output')
	args = parser.parse_args()
	log_locations = get_log_locations(args.directory)
	result, timing_result = parsealllogs(log_locations)

	with open(args.output_file, 'w') as output:
		json.dump(result, output)
	with open(args.timing_output_file, 'w') as output:
		json.dump(timing_result, output)
