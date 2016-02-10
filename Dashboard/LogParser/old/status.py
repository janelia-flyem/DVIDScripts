from libdvid import DVIDNodeService, ConnectionMethod
import httplib
import MySQLdb as sql
import argparse
import json
import pprint
from urlparse import urlsplit

status_cvs = {'Hard to trace': 'hard_to_trace',
			 'Not examined': 'not_examined', 
			 'Traced': 'traced', 
			 'Orphan': 'orphan', 
			 'Partially Traced': 'partially_traced',
			 'Finalized': 'finalized',
}
name_cvs = {
	'KC': 'kenyon_cell',
	'Irrelevant': 'irrelevant',
	'orphan': 'orphan',
	'Others': 'other',
}


def connectDB(dev=False):
	"""
	Connects to the mad database
	input: dev = (t/f)
	returns: cursor and database connection
	"""
	if dev:
		print "clustrix1"
		db = sql.connect(host='clustrix1', user='madApp', passwd='m@dApp', db='mad')
	else:
		db = sql.connect(host='clustrix2', user='madApp', passwd='m@jung@s@urusW', db='mad')
	c = db.cursor()
	return c, db

def bodyStatusFromDVID(node_service, connection, uuid, dataname):
	status = {'Hard to trace': 0,
				 'Not examined': 0,
				 'Traced': 0,
				 'Orphan': 0,
				 'Partially Traced': 0,
				 'Finalized': 0,
			}
	user_status = {}
	#get keys
	response_body = node_service.custom_request( bodies + "/keys", "", ConnectionMethod.GET )
	annotation_keys = json.loads(response_body)
	print "Total bodies", len(annotation_keys)
	annotation_keys = [k for k in annotation_keys if k.isdigit() and not isDeadBody(connection, uuid, dataname, k)]
	print "Live bodies", len(annotation_keys)
	#for each key get status and add to dictionary
	named = {
		'KC' : {'Hard to trace': 0,
				 'Not examined': 0,
				 'Traced': 0,
				 'Orphan': 0,
				 'Partially Traced': 0,
				 'Finalized': 0,
		},
		'Irrelevant' : {'Hard to trace': 0,
				 'Not examined': 0,
				 'Traced': 0,
				 'Orphan': 0,
				 'Partially Traced': 0,
				 'Finalized': 0,
		},
		'orphan' : {'Hard to trace': 0,
				 'Not examined': 0,
				 'Traced': 0,
				 'Orphan': 0,
				 'Partially Traced': 0,
				 'Finalized': 0,
		},
		'Others' : {'Hard to trace': 0,
				 'Not examined': 0,
				 'Traced': 0,
				 'Orphan': 0,
				 'Partially Traced': 0,
				 'Finalized': 0,
		}
	}
	for k in annotation_keys:
		annotation = node_service.get(bodies, str(k))
		annotation_JSON = json.loads(annotation)
		if 'status' in annotation_JSON:
			s = annotation_JSON['status']
			if s not in status:
				status[s] = 0
			status[s] += 1
			if load_named:
				if "name" in annotation_JSON:
					# for-else, else executes if for loop not exited through break
					for k in named:
						if k in annotation_JSON['name']:
							named[k][s] += 1
							break
					# only executes if the neuron has a non-standard name
					else:
						if s != 'Not examined':
							named['Others'][s] += 1
			if 'user' in annotation_JSON:
				user = annotation_JSON['user']
				if user not in user_status:
					user_status[user] = {
						'Hard to trace': 0,
						'Not examined': 0,
						'Traced': 0,
						'Orphan': 0,
						'Partially Traced': 0,
						'Finalized': 0,
					}
				user_status[user][s] += 1
		else:
			status['Not examined'] += 1
	pprint.pprint(status)
	pprint.pprint(named)
	return status, user_status, named

def loadStatusToMAD(cursor, media_id, status):
	#for each status, load into MAD
	for k,v in status_cvs.items():
		cv_term = getCvTerm(cursor, "body_status", v)
		insertAnnotation(cursor, media_id, cv_term, status[k])

def loadNamedBodyStatusToMAD(cursor, media_id, status):
	#for each status, load into MAD
	for k,v in name_cvs.items():
		cv_term = getCvTerm(cursor, "body_type", v)
		annotation_id = insertAnnotation(cursor, media_id, cv_term, 0)
		for k2, v2 in status_cvs.items():
			type_id = getCvTerm(cursor, "body_status", v2)
			insertAnnotationProperty(cursor, annotation_id, type_id, status[k][k2])

def loadUserStatusToMAD(cursor, media_id, status):
	#for each status, load into MAD
	statusCVID = {}
	for k,v in status_cvs.items():
		cv_term = getCvTerm(cursor, "body_status", v)
		statusCVID[k] = cv_term
	for user in user_status:
		user_id = getUserID(cursor, user)
		if user_id:
			for k,v in statusCVID.items():
				insertAnnotation(cursor, media_id, v, user_status[user][k], user_id)
		else:
			print "Error, no user_id in MAD for %s" % (user)

	
def getUserID(cursor, user):
	query = "select id from user where name = %s"
	cursor.execute(query, (user,))
	try:
		results = cursor.fetchone()[0]
		return results
	except:
		return None

def insertAnnotation(cursor, media_id, type_id, value, user_id = None):
	if user_id:
		query = "insert into annotation set media_id = %s, type_id = %s, value= %s, is_current=1, user_id=%s"
		cursor.execute(query, (media_id, type_id, value, user_id))
	else:
		query = "insert into annotation set media_id = %s, type_id = %s, value= %s, is_current=1"
		cursor.execute(query, (media_id, type_id, value))
	return cursor.lastrowid

def insertAnnotationProperty(cursor, annotation_id, type_id, value):
	query = "insert into annotation_property set annotation_id = %s, type_id = %s, value= %s" 
	cursor.execute(query, (annotation_id, type_id, value))

def getMediaID(cursor, mediaName):
	query = "Select id from media where name=%s" 
	cursor.execute(query, (mediaName,))
	results = cursor.fetchone()[0]
	return results

def getCvTerm(cursor, cv, cv_term):
	cursor.execute("select id from cv_term_vw where cv=%s and cv_term=%s" , (cv, cv_term))
	return cursor.fetchone()[0]

# def isDeadBody(service, dataname, body_id):
# 	if str(body_id) == '0':
# 		return True
# 	try:
# 		body_exists = node_service.body_exists(dataname, body_id)
# 		return not body_exists
# 	except:
# 		return True
		
def isDeadBody(connection, uuid, dataname, body_id):
	if str(body_id) == '0':
		return True
	url = "/api/node/" + uuid + "/" + dataname + "/"
	fullUrl = url + str(body_id)
	try:
		connection.request("GET", fullUrl)
		response = connection.getresponse()
		s = response.read()
		if len(s) <= 12:
			return True
		else:
			return False 
	except:
		return True

def getUUID(cursor, media):
	query = 'select value from media_property_vw where media = %s and type = "dvid_uid"'
	cursor.execute(query, (media,))
	results = cursor.fetchone()[0]
	return results

def getDVIDURL(cursor, media):
	query = 'select value from media_property_vw where media = %s and type = "dvid_url"'
	cursor.execute(query, (media,))
	results = cursor.fetchone()[0]
	return results

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Load Mad Data")
	parser.add_argument('--debug', dest='debug', action='store_true', default=False, help='Flag, verbose output if set')
	parser.add_argument('--dev', dest='dev', action='store_true', default=False, help='Flag, runs against dev database if set')
	parser.add_argument('--insert', dest='insert', action='store_true', default=False, help='Flag, commits to database if set')
	parser.add_argument('--named', dest='load_named', action='store_true', default=True, help='Flag, loads named stats if set')
	parser.add_argument('--uuid', dest='uuid', action='store', default='', help='Which uuid to use in DVID')
	parser.add_argument('--labelvol', dest='labelvol', action='store', default='bodies3/sparsevol-coarse', help='Which dataname contains the sparsevol')
	parser.add_argument('--annotations', dest='bodies', action='store', default='bodies3_annotations', help='Which dataname contains the bodies annotations')
	parser.add_argument('--user', dest='user', action='store_true', default=False, help='Flag, load data by user as well as in aggregate')
	parser.add_argument('--dvid', dest='dvid', action='store', default=False, help='Which DVID server to use')
	parser.add_argument('--media', dest='media', action='store', default='MB-Z0613-06', help='Media ID to store annotations as')
	parser.add_argument('--orphan_media', dest='orphan_media', action='store', default='MB-Z0613-06_Orphan_Links', help='Media ID to store annotations as')
	
	arg = parser.parse_args()
	debug = arg.debug
	dev = arg.dev
	insert = arg.insert
	uuid = arg.uuid
	dvid = arg.dvid
	load_user = arg.user
	media = arg.media
	orphan_media = arg.orphan_media
	labelvol = arg.labelvol
	load_named = arg.load_named
	bodies = arg.bodies

	#connect to MAD
	
	if not uuid:
		c,db = connectDB(dev)
		uuid = getUUID(c, orphan_media)
		c.close()
		db.close()
	print "UUID", uuid

	if not dvid:
		c,db = connectDB(dev)
		dvid = getDVIDURL(c, orphan_media)
		c.close()
		db.close()
	print "DVID", dvid

	#connect to DVID
	node_service = DVIDNodeService(dvid, uuid)
	dvid_split = urlsplit(dvid)
	connection_dvid = dvid_split.netloc
	connection = httplib.HTTPConnection(connection_dvid, timeout=10.0)

	#build dictionary of status
	status, user_status, named_status = bodyStatusFromDVID(node_service, connection, uuid, labelvol)

	c, db = connectDB(dev)
	#get correct media
	media_id = getMediaID(c, media)
	#load status lines
	loadStatusToMAD(c, media_id, status)
	if load_named:
		loadNamedBodyStatusToMAD(c, media_id, named_status)
	#load user_status to mad
	if load_user:
		loadUserStatusToMAD(c, media_id, user_status)

	if (insert):
		db.commit()
	else:
		db.rollback()
	c.close()
	db.close()

	
