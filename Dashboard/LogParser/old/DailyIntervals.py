import json
import argparse

import neutu_log_module as nt


def getIntervalData(location):
	'''
	Goes through file and gets working intervals
	input: log directory
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
	data = {}
	log_locations = nt.get_log_locations(location)
	for log in log_locations:
		if log['user'] not in data:
			data[log['user']] = []
		chunk = []
		for path in log['paths']:	
			with open(path) as fi:	
				old_date = None
				for line in fi:
					line_date = nt.gettimestamp(line)
					if not line_date:
						continue
					if not old_date and line_date:
						old_date = line_date.date()
					if old_date and old_date != line_date.date():
						if len(chunk):
							date_string = old_date.strftime('%Y-%m-%d')
							data[log['user']].append({'date': date_string,'data': nt.getworkingintervalsforchunk(chunk)})
						chunk = []
					chunk.append(line)
					old_date = line_date.date()
		if len(chunk) :
			date_string = old_date.strftime('%Y-%m-%d')
			data[log['user']].append({'date': date_string,'data': nt.getworkingintervalsforchunk(chunk)})
	return data



if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Get Hourly Work Snapshot")
	parser.add_argument('--log_directory', dest='directory', action='store', default='/Users/weaverc10/Desktop/neutu_log/', help='Directory that contains log files')
	parser.add_argument('--output', dest='output_file', action='store', default='neutu_actions.json', help='File Name for output')

	args = parser.parse_args()
	data = getIntervalData(args.directory)
	with open(args.output_file, 'w') as fi:
		json.dump(data, fi)