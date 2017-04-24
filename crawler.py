from collections import deque
import json
from re import findall
from time import time

def crawl(api, origin, fifo, max_following, max_followers, max_collect_users, max_collect_media):
	user_id = origin['user']['pk']
	profile = origin
	visit_profile(api, user_id, max_collect_media)

	# followers = []
	# results = api.user_followers(user_id)
	# followers.extend(results.get('users', []))
	# next_max_id = results.get('next_max_id')
	# while next_max_id and len(followers) < max_followers:
	# 	results = api.user_followers(user_id, max_id=next_max_id)
	# 	followers.extend(results.get('users', []))
	# 	next_max_id = results.get('next_max_id')

	# followers.sort(key=lambda x: x['pk'])
	# # print list of user IDs
	# print(json.dumps([u['username'] for u in followers], indent=2))
	pass

def visit_profile(api, user_id, max_collect_media):
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
	min_timestamp = int(time() - 60*60*24*30)
	feed = _get_posts(api, user_id, max_collect_media, min_timestamp) # should get more images here.

	posts = [visit_media(api, post) for post in feed]
	processed_profile['posts'] = list(filter(lambda x: not x is None, posts))
	with open('profiles/' + str(user_id) + '.json', 'w') as file:
		file.write(json.dumps(processed_profile, indent=2))

def visit_media(api, post):
	if post['media_type'] != 1: # If post is not a single image media
		return None
	keys = post.keys()
	# print(keys, post['caption'], 'caption' in post.keys())
	# print('text' in post['caption'])
	# print('text' in post['caption'].keys())
	# print(post['caption']['text'])
	processed_media = {
		'date' : post['taken_at'],
		'pic_url' : post['image_versions2']['candidates'][0]['url'],
		'like_count' : post['like_count'] if 'like_count' in keys else 0,
		'comment_count' : post['comment_count'] if 'comment_count' in keys else 0,
		'caption' : post['caption']['text'] if 'caption' in keys and post['caption'] is not None else ''
	}
	processed_media['tags'] = findall(r'#[A-Za-z0-9]*', processed_media['caption'])
	return processed_media

def _get_posts(api, user_id, max_collect_media, min_timestamp=None):
	feed = []
	results = api.user_feed(user_id)
	feed.extend(results.get('items', []))
	# print(feed)
	next_max_id = results.get('next_max_id')
	print(next_max_id)
	while next_max_id and len(feed) < max_collect_media:
		print("next_max_id", next_max_id, "len(feed) < max_collect_media", len(feed) < max_collect_media )
		results = api.user_feed(user_id, max_id=next_max_id)
		feed.extend(results.get('items', []))
		next_max_id = results.get('next_max_id')

	return feed

def _get_community(api, user_id, max_following, max_followers):
	following = []
	results = api.user_following(user_id)
	following.extend(results.get('users', []))
	next_max_id = results.get('next_max_id')
	while next_max_id and len(following) < max_following:
		results = api.user_following(user_id, max_id=next_max_id)
		following.extend(results.get('users', []))
		next_max_id = results.get('next_max_id')

	followers = []
	results = api.user_followers(user_id)
	followers.extend(results.get('users', []))
	next_max_id = results.get('next_max_id')
	while next_max_id and len(followers) < max_followers:
		results = api.user_followers(user_id, max_id=next_max_id)
		followers.extend(results.get('users', []))
		next_max_id = results.get('next_max_id')

	return following, followers