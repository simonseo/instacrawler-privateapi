import json
import os.path
import argparse
from collections import deque

try:
	from instagram_private_api import (
		Client, __version__ as client_version)
except ImportError:
	import sys
	sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
	from instagram_private_api import (
		Client, __version__ as client_version)
from crawler import crawl


if __name__ == '__main__':
	# Example command:
	# python examples/savesettings_logincallback.py -u "yyy" -p "zzz" -target "names.txt"
	parser = argparse.ArgumentParser(description='Crawling')
	parser.add_argument('-u', '--username', dest='username', type=str, required=True)
	parser.add_argument('-p', '--password', dest='password', type=str, required=True)
	parser.add_argument('-f', '--targetfile', dest='targetfile', type=str, required=False)
	parser.add_argument('-t', '--target', dest='target', type=str, required=False)
	# parser.add_argument('-debug', '--debug', action='store_true')

	args = parser.parse_args()
	max_followers = 20                   # How many followers per user to collect
	max_following = 20                     # how many follows to collect per user
	max_collect_media = 100              # how many media items to be collected per person ?
	max_collect_users = 20               # how many users in all to collect.
	fifo = deque([])

	# Connect
	try:
		if args.target:
			fifo.extend([args.target])
		# elif args.targetfile:
		# 	with open(args.targetfile, 'r') as file:
		# 		fifo.extend([line in file][1:])
		else:
			raise Exception('No crawl target given. Provide a username with -t option or file of usernames with -f')

		print('Client version: %s' % client_version)
		api = Client(args.username, args.password)
		origin = api.username_info(fifo.popleft()) #only the first element can be a name, will be id from now on
	except Exception as e:
		print("unable to initiate crawl", e)
	else:
		user_id = origin['user']['pk']
		username = origin['user']['username']
		print('Set Origin to', username, 'with ID', user_id)

	# open graph files
	if not os.path.exists('./userdata/'):
		os.makedirs('userdata')            
	edges = open("./userdata/edges.csv",'a')
	user_details = open ("./userdata/user_details.csv",'a')
	
	

	crawl(api, origin, fifo, max_following, max_followers, max_collect_users, max_collect_media)

	# close files
	
	edges.close()
	user_details.close()



  # for username in usernames:
  #   print('Extracting information from ' + username)
  #   information = extract_information(browser, username)

  #   with open('./profiles/' + username + '.json', 'w') as fp:
  #     json.dump(information, fp)

