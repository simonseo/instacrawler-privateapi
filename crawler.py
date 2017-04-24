from collections import deque
import json
from re import findall
from time import time
from random import sample, shuffle

def crawl(api, origin, fifo, config):
	fifo.append(origin['user']['pk'])
	visited_nodes = []

	while len(visited_nodes) < config['max_collect_users'] and len(fifo) > 0:
		user_id = fifo.popleft()
		if user_id in visited_nodes: continue
		visit_profile(api, user_id, config)
		visited_nodes.append(user_id)
		following, followers = _get_community(api, user_id, config)
		fifo.extend(randselect([u['pk'] for u in following], config['max_following']))
		fifo.extend(randselect([u['pk'] for u in followers], config['max_followers']))
		for user_id in fifo:
			try:
				float(user_id)
			except ValueError:
				raise Exception('wrong value put into que')
		



	# followers.sort(key=lambda x: x['pk'])
	# # print list of user IDs
	# print(json.dumps([u['username'] for u in followers], indent=2))
	pass

def visit_profile(api, user_id, config):
	profile = api.user_info(user_id)
	processed_profile = {
		'user_id' : user_id,
		'username' : profile['user']['username'],
		'full_name' : profile['user']['full_name'],
		'profile_pic_url' : profile['user']['profile_pic_url'],
		'media_count' : profile['user']['media_count'],
		'follower_count' : profile['user']['follower_count'],
		'following_count' : profile['user']['following_count'],
	}
	feed = _get_posts(api, user_id, config)
	posts = [visit_media(api, post) for post in feed]
	processed_profile['posts'] = list(filter(lambda x: not x is None, posts))
	with open('profiles/' + str(user_id) + '.json', 'w') as file:
		json.dump(processed_profile, file, indent=2)

def visit_media(api, post):
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
	processed_media['tags'] = findall(r'#[A-Za-z0-9]*', processed_media['caption'])
	return processed_media

def _get_posts(api, user_id, config):
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

def _get_community(api, user_id, config):
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

	return following, followers

def randselect(list, num):
	l = len(list)
	if l <= num:
		return shuffle(list)
	if l > 5*num: 
		return sample(list[:5*num], num)
