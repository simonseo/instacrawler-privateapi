from collections import deque
import json
from re import findall

def crawl(api, origin, max_following, max_followers, max_collect_users, max_collect_media):
	user_id = origin['user']['pk']
	profile = origin
	visit_profile(api, profile)

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

def visit_profile(api, profile):
	user_id = profile['user']['pk']
	processed_profile = {
		'user_id' : user_id,
		'username' : profile['user']['username'],
		'full_name' : profile['user']['full_name'],
		'profile_pic_url' : profile['user']['profile_pic_url'],
		'media_count' : profile['user']['media_count'],
		'follower_count' : profile['user']['follower_count'],
		'following_count' : profile['user']['following_count'],
	}
	feed = api.user_feed(user_id) # should get more images here.
	posts = (visit_media(api, post) for post in feed['items'])
	processed_profile['posts'] = list(filter(lambda x: x is not None, posts))

	with open('profiles/' + str(user_id) + '.json', 'w') as file:
		file.write(json.dumps(processed_profile, indent=2))

def visit_media(api, post):
	if post['media_type'] != 1: # If post is not a single image media
		return None
	processed_media = {
		'date' : post['taken_at'],
		'pic_url' : post['image_versions2']['candidates'][0]['url'],
		'like_count' : post['like_count'],
		'comment_count' : post['comment_count'],
		'caption' : post['caption']['text'] if post['caption'] else ''
	}
	processed_media['tags'] = findall(r'#[A-Za-z0-9]*', processed_media['caption'])
	return processed_media
