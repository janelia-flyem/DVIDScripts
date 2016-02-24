import argparse
import json
from libdvid import DVIDNodeService, ConnectionMethod 
from libdvid._dvid_python import DVIDException

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="")
	parser.add_argument('--insert', dest='insert', action='store_true', default=False, help='Flag, loads to DVID if set')
	parser.add_argument('--uuid', dest='uuid', action='store', default='', help='Which uuid to use in DVID')
	parser.add_argument('--dvid', dest='dvid', action='store', default='', help='Which DVID server to use')
	parser.add_argument('--key-name', dest='key_name', action='store', default='dashboard', help='Name of key to store data under in DVID')
	parser.add_argument('--key-value-store', dest='key_value_store', action='store', default='external_dashboard', help='Name of keyvalue data instance to put key-values under')
	parser.add_argument('--input', dest='input', action='store', default='', help='Path to input JSON')


	args = parser.parse_args()
	#connect to DVID
	node_service = DVIDNodeService(args.dvid, args.uuid)

	
	#If key doesn't exist create it
	key_info_url = '/{kv_name}/info'.format(kv_name=args.key_value_store)
	try:
		node_service.custom_request(key_info_url, '', ConnectionMethod.GET)
	except DVIDException:
		if args.insert:
			node_service.create_keyvalue(args.key_value_store)

	# Read in data
	with open(args.input) as fi:
		data = json.load(fi)

	# Replace data in key value
	if args.insert:
		node_service.put(args.key_value_store, args.key_name, json.dumps(data))

	if args.insert:
		assert node_service.get(args.key_value_store, args.key_name)




