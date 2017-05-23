#!/usr/bin/python
# -*- coding: utf-8 -*- 
# @File Name: filter_profile.py
# @Created:   2017-05-19 20:10:56  Simon Myunggun Seo (simon.seo@nyu.edu) 
# @Updated:   2017-05-20 08:41:30  Simon Seo (simon.seo@nyu.edu)

'''This script was created to deal with profiles that have less than 10 posts.'''

import os
import json

rootdir = './profiles_3'
for subdir, dirs, files in os.walk(rootdir):
	for file in files:
		#print os.path.join(subdir, file)
		filepath = subdir + os.sep + file
		# filepath = "profiles/1057969838.json"
		if filepath.endswith(".json"):
			with open(filepath, 'r') as fp:
				print (filepath)
				profile = json.load(fp)
			l = len(profile['posts'])
			if l != 10:
				print('removing {}'.format(filepath))
				os.remove(filepath)
