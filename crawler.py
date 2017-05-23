import json
import os
from collections import deque
from re import findall
from time import time
from util import randselect, byteify, file_to_list
import csv

def crawl(api, origin,config, visited_nodes, skipped_nodes):
	print('Crawling started at origin user', origin['user']['username'], 'with ID', origin['user']['pk'])
	que = deque([])
	que.append(origin['user']['pk'])

	while len(visited_nodes) < config['max_collect_users']:
		user_id = que.popleft()
		if user_id in visited_nodes or user_id in skipped_nodes:
			print('Already visited or skipped')
			continue
		if visit_profile(api, user_id, config):
			visited_nodes.append(user_id)
		else:
			skipped_nodes.append(user_id)
		following, followers = get_community(api, user_id, config)
		extend_que(following, followers, que, config)
		if len(que) <= 0:
			raise Exception('Que empty!')

def visit_profile(api, user_id, config):
	while True:
		try:
			profile = api.user_info(user_id)
			print('Visiting:', profile['user']['username'])
			processed_profile = {
				'user_id' : user_id,
				'username' : profile['user']['username'],
				'full_name' : profile['user']['full_name'],
				'profile_pic_url' : profile['user']['profile_pic_url'],
				'media_count' : profile['user']['media_count'],
				'follower_count' : profile['user']['follower_count'],
				'following_count' : profile['user']['following_count'],
				'posts' : []
			}
			feed = get_posts(api, user_id, config)
			posts = [beautify_post(api, post) for post in feed]
			posts = list(filter(lambda x: not x is None, posts))
			if len(posts) < config['min_collect_media']:
				return False
			else:
				processed_profile['posts'] = posts[:config['max_collect_media']]

			if not os.path.exists(config['profile_path'] + os.sep): os.makedirs(config['profile_path'])  
			with open(config['profile_path'] + os.sep + str(user_id) + '.json', 'w') as file:
				json.dump(processed_profile, file, indent=2)
		except Exception as e:
			print('exception while visiting profile', e)
			if api.friendships_show(user_id)['is_private']:
				return False
			if str(e) == '-':
				return False
		else:
			return True

def beautify_post(api, post):
	if post['media_type'] != 1: # If post is not a single image media
		return None
	keys = post.keys()
	processed_media = {
		'date' : post['taken_at'],
		'pic_url' : post['image_versions2']['candidates'][0]['url'],
		'like_count' : post['like_count'] if 'like_count' in keys else 0,
		'comment_count' : post['comment_count'] if 'comment_count' in keys else 0,
		'caption' : post['caption']['text'] if 'caption' in keys and post['caption'] is not None else ''
	}
	processed_media['tags'] = findall(r'#[^#\s]*', processed_media['caption'])
	# print(processed_media['tags'])
	return processed_media

def get_posts(api, user_id, config):
	feed = []
	results = api.user_feed(user_id, min_timestamp=config['min_timestamp'])
	feed.extend(results.get('items', []))

	if config['min_timestamp'] is not None: return feed

	next_max_id = results.get('next_max_id')
	while next_max_id and len(feed) < config['max_collect_media']:
		print("next_max_id", next_max_id, "len(feed) < max_collect_media", len(feed) < config['max_collect_media'] )
		results = api.user_feed(user_id, max_id=next_max_id)
		feed.extend(results.get('items', []))
		next_max_id = results.get('next_max_id')

	return feed

def get_community(api, user_id, config):
	while True:
		try:
			following = []
			results = api.user_following(user_id)
			following.extend(results.get('users', []))
			next_max_id = results.get('next_max_id')
			while next_max_id and len(following) < config['max_following']:
				results = api.user_following(user_id, max_id=next_max_id)
				following.extend(results.get('users', []))
				next_max_id = results.get('next_max_id')

			followers = []
			results = api.user_followers(user_id)
			followers.extend(results.get('users', []))
			next_max_id = results.get('next_max_id')
			while next_max_id and len(followers) < config['max_followers']:
				results = api.user_followers(user_id, max_id=next_max_id)
				followers.extend(results.get('users', []))
				next_max_id = results.get('next_max_id')

			print(user_id, 'has', len(following), 'following and', len(followers), 'followers')
			return following, followers
			following, followers = get_community(api, user_id, config)
		except Exception as e:
			print('exception while getting community', e)
		else:
			break

def extend_que(following, followers, que, config):
	try:
		if config['search_algorithm'] == 'BFS':
			que.extend(randselect([u['pk'] for u in following], config['max_following']))
			que.extend(randselect([u['pk'] for u in followers], config['max_followers']))
		elif  config['search_algorithm'] == 'DFS':
			que.extendleft(randselect([u['pk'] for u in following], config['max_following']))
			que.extendleft(randselect([u['pk'] for u in followers], config['max_followers']))
		else:
			raise Exception('Please provide proper search algorithm in config (BFS or DFS)')
	except Exception as e:
		print('exception while extending que', e)
	for user_id in que:
		try:
			float(user_id)
		except ValueError:
			raise Exception('wrong value put into que')
