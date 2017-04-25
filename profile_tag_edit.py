'''This script was created to deal with posts that had tags in the form of #smth#smth, without a space.
The current crawler should handle such cases properly.'''

import os
import json

rootdir = './profiles'
for subdir, dirs, files in os.walk(rootdir):
	for file in files:
		#print os.path.join(subdir, file)
		filepath = subdir + os.sep + file
		# filepath = "profiles/1057969838.json"
		if filepath.endswith(".json"):
			with open(filepath, 'r') as fp:
				print (filepath)
				profile = json.load(fp)
			for post in profile['posts']:
				temp = []
				d = '#'
				for tag in post['tags']:
					temp.extend([d+e for e in tag.split(d) if e])
				post['tags'] = temp
			with open(filepath, 'w') as fp:
				json.dump(profile, fp, indent=2)
