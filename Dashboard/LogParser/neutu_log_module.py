# std lib
import os
import re
from datetime import datetime, timedelta

# note that the milliseconds portion is dropped
timestampformat = "%Y-%m-%dT%H:%M:%S.%f"
timestamplength = len("2015-10-13T09:19:36.729")
newtimestampformat = "%Y%m%d %H:%M"
# useful:
secondsperday = 24 * 60 * 60

# idle threshold for working time; default is 10 minutes
defaultworkingthreshold = 10 * 60

# idle threshold for session time; default is 30 minutes
defaultsessionthreshold = 30 * 60

# length of log level statement (INFO, ERROR, etc.)
loglevellength = 6

def getDVIDnodealias(server, port, uuid):
	api_url = "http://%s:%s/api/repo/%s/info" % (server, port, uuid)
	try:
		response = urllib2.urlopen(api_url, timeout=10.0)
		info_json = json.load(response)
		return info_json['Alias']
	except urllib2.URLError:
		return "Unknown"

def getloglocations(directory):
	"""
	Generate for logs per user. Yields dictionary of user and paths associated
	with that user
	input: directory
	output: generator {user:username, paths:[list of paths sorted earliest -> latest]}
	"""
	for w in os.walk(directory):
		if 'log.txt' in w[2]:
			username = os.path.basename(w[0])
			yield {
				'user': username,
				'paths': [os.path.join(w[0], fn) for fn in sortloglist(w[2]) ]
			}

def gettimestamp(line):
	"""
	Gets time a line was created
	input: neutu log line
	output: datetime for line
	"""
	try:
		timestamp = line[0:timestamplength]
		return datetime.strptime(timestamp, timestampformat)
	except ValueError:
		line = line[loglevellength:]
		timestamp = line[0:timestamplength]
		try:
			return datetime.strptime(timestamp, timestampformat)
		except ValueError:
			return None

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
	timestamps = [t for t in timestamps if t is not None]
	intervals = getintervals(timestamps)
	start = timestamps[0]
	for i in range(len(timestamps) - 1):
		if intervals[i].total_seconds() > defaultworkingthreshold:
			start = timestamps[i+1]
	#print len(timestamps), len(intervals)
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

def getworkingintervalsforchunk(data):
	"""
	given a list of data lines, return two lists of t1, dt corresponding
	to working and idle times
	
	input: data
	output: two lists of (t1, dt) intervals, working and idle
	"""
	
	timestamps = [gettimestamp(line[loglevellength:]) for line in data]
	timestamps = [t for t in timestamps if t is not None]
	intervals = getintervals(timestamps)
	start = timestamps[0]
	working_intervals = []
	date_fmt = '%Y-%m-%d %H:%M'
	for i in range(len(timestamps) - 1):
		if intervals[i].total_seconds() > defaultworkingthreshold:
			working_intervals.append({
				'start': start.strftime(date_fmt),
				'stop': timestamps[i].strftime(date_fmt),
				'type': 'working',
				})
			start = timestamps[i+1]
	working_intervals.append({
		'start': start.strftime(date_fmt),
		'stop': timestamps[-1].strftime(date_fmt),
		'type': 'working',
	})
	return working_intervals

def parsefortime(chunk):
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

def getbookmarkid(line):
	bookmarkid = None
	matches = re.search("ID: (\d+) is clicked", line)
	if matches and matches.group(1):
		bookmarkid = matches.group(1)
	return bookmarkid

def loadchunks(lines):
	"""
	give a list of lines concatenated from multiple log files, find
	the natural chunks, defined as starting with a session load or
	a new day 
	
	input: iterable over log lines
	output: iterator that returns lists of lines belonging to one "chunk"
	"""
	chunk = []
	oldline = None
	date_pattern = re.compile("^20[0-9][0-9]-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}")

	for line in lines:
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

def daychunks(lines):
	"""
	give a list of lines concatenated from multiple log files, find
	the chunks for each new day 
	
	input: iterable over log lines
	output: iterator that returns lists of lines belonging to one "chunk"
	"""
	chunk = []
	oldline = None
	date_pattern = re.compile("^20[0-9][0-9]-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}")

	for line in lines:
		#strip off loglevel
		l = line[loglevellength:].rstrip()
		#check if line starts with timestamp, if not discard
		if (date_pattern.match(l)):
			if oldline:
				# when to begin a new chunk?
				if not sameday(oldline, l):
					yield chunk
					chunk = []				
			oldline = l
			chunk.append(line)
	yield chunk

def sameday(oldline, line):
	oldtime = gettimestamp(oldline)
	newtime = gettimestamp(line)
	if oldtime.day != newtime.day:
		return False
	else:
		return True