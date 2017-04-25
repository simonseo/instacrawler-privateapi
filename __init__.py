import json
import os.path
import argparse
from time import time
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
	config = {
		'search_algorithm' : 'BFS',               # Possible values: BFS, DFS
		'profile_path' : './profiles',              # Path where output data gets saved
		'max_followers' : 20,                    # How many followers per user to collect
		'max_following' : 15,                    # how many follows to collect per user
		'max_collect_media' : 50,                # how many media items to be collected per person. If time is specified, this is ignored
		'max_collect_users' : 1,               # how many users in all to collect.
		'min_timestamp' : int(time() - 60*60*24*30*2)         # up to how recent you want the posts to be in seconds
		# 'min_timestamp' : None
	}
	que = deque([])

	# Connect
	try:
		if args.target:
			origin_names = [args.target]
		elif args.targetfile:
			with open(args.targetfile, 'r') as file:
				origin_names = [line.strip().split() for line in file]
		else:
			raise Exception('No crawl target given. Provide a username with -t option or file of usernames with -f')

		print('Client version: %s' % client_version)
		print(origin_names)
		api = Client(args.username, args.password)
	except Exception as e:
		raise Exception("Unable to initiate API:", e)
	else:
		print("Initiating API")

	# open graph files
	if not os.path.exists('./userdata/'):
		os.makedirs('userdata')            
	edges = open("./userdata/edges.csv",'a')
	user_details = open ("./userdata/user_details.csv",'a')

	for origin in (api.username_info(username) for username in origin_names):
		crawl(api, origin, que, config)

	# close files
	edges.close()
	user_details.close()

