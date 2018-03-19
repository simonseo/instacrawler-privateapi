import json
import os.path
import argparse
import multiprocessing as mp
import csv
from time import time
from collections import deque
from util import file_to_list
from crawler import crawl
try:
	from instagram_private_api import (
		Client, __version__ as client_version)
except ImportError:
	import sys
	sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
	from instagram_private_api import (
		Client, __version__ as client_version)


if __name__ == '__main__':
	# Example command:
	# python examples/savesettings_logincallback.py -u "yyy" -p "zzz" --targetfile "names.txt"
	parser = argparse.ArgumentParser(description='Crawling')
	parser.add_argument('-u', '--username', dest='username', type=str, required=True)
	parser.add_argument('-p', '--password', dest='password', type=str, required=True)
	parser.add_argument('-f', '--targetfile', dest='targetfile', type=str, required=False)
	parser.add_argument('-t', '--target', dest='target', type=str, required=False)
	parser.add_argument('--hashtag', dest='use_hashtag', action='store_true')
	parser.set_defaults(use_hashtag=False)

	args = parser.parse_args()
	config = {
		'search_algorithm' : 'BFS',               # Possible values: BFS, DFS
		'profile_path' : './profiles',              # Path where output data gets saved
		'max_followers' : 10,                    # How many followers per user to collect
		'max_following' : 15,                    # how many follows to collect per user
		'min_collect_media' : 10,                # how many media items to be collected per person/hashtag. If time is specified, this is ignored
		'max_collect_media' : 10,                # how many media items to be collected per person/hashtag. If time is specified, this is ignored
		'max_collect_users' : 1000,               # how many users to collect in total.
		# 'min_timestamp' : int(time() - 60*60*24*30*2)         # up to how recent you want the posts to be in seconds. If you do not want to use this, put None as value
		'min_timestamp' : None
	}

	try:
		if args.target:
			origin_names = [args.target]
		elif args.targetfile:
			origin_names = file_to_list(args.targetfile)
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
	v = "./userdata/visited.csv"
	open(v,'a').close()
	visited_nodes = mp.Manager().list([int(node) for node in file_to_list(v)])
	s = "./userdata/skipped.csv"
	open(s,'a').close()
	skipped_nodes = mp.Manager().list([int(node) for node in file_to_list(s)])

	try:
		jobs = []
		for origin in (api.username_info(username) for username in origin_names):
			# crawl(api, origin, config, visited_nodes, skipped_nodes)
			p = mp.Process(target=crawl, args=(api, origin, config, visited_nodes, skipped_nodes))
			jobs.append(p)
			p.start()
	except KeyboardInterrupt:
		print('Jobs terminated')
	except Exception as e:
		print(e)
	for p in jobs:
		p.join()

	with open(v, "w") as output:
		writer = csv.writer(output, lineterminator='\n')
		writer.writerow(visited_nodes)
	with open(s, "w") as output:
		writer = csv.writer(output, lineterminator='\n')
		writer.writerow(skipped_nodes)
