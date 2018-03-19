# Instagram Crawler
This crawler was made because most of the crawlers out there seems to either require a browser or a developer account. This Instagram crawler utilizes a private API of Instagram and thus no developer account is required. However, it needs your Instagram account information as it uses your user endpoints. 

Instagram may or may not approve of this method. It is known to regularly shut down user accounts that are suspected of traffic hoarding. Use at your own risk.

This README assumes, to an extent, the reader's knowledge of [graphs](https://en.wikipedia.org/wiki/Graph_(discrete_mathematics)) and [graph search algorithms](https://en.wikipedia.org/wiki/Graph_traversal#Graph_traversal_algorithms). Regardless, there shouldn't be a big problem understanding it. 

## Installation
First install [Instagram Private API](https://github.com/ping/instagram_private_api). Kudos for a great project!
```sh
$ pip install git+https://github.com/ping/instagram_private_api.git@1.2.7
```

Then download or clone this project into a folder.
```sh
$ git clone https://github.com/simonseo/instacrawler-privateapi.git
```

[Sign up to Instagram](https://www.instagram.com/) if you don't have an account. Take note of your username and password.


## Get Crawlin'

Now if you try to run `__init__.py` in the project folder from a shell, it'll provide you with the command options. If this shows up, everything probably works. Also try `python __init.py__ -h` for more information regarding the options.
```sh
$ python __init__.py
usage: __init__.py [-h] -u USERNAME -p PASSWORD [-f TARGETFILE] [-t TARGET]
```

To get crawlin', you need to provide your 
1. Instagram username
1. Instagram passwor
1. either an Instagram ID (target `-t`) or a text file of Instagram IDs in each row (targetfile `-f`)

### Examples
#### Single Root Node
In the case you want to start at one specific user node, provide the ID/username/handle with the option `-t`. `selenagomez` is a good place to start because this account is one of the most followed account.
```sh
$ python __init__.py -u <yourUsername> -p <yourPassword> -t selenagomez
```

#### Multiple Root Nodes
In the case you want to crawl from multiple user nodes, list the IDs in a separate file and pass the filename with the `-f` option. Example:
```sh
$ python __init__.py -u <yourUsername> -p <yourPassword> -f "people I stalk.txt"
```

In `people I stalk.txt` you should have accounts that you want to start at. Here is an example of what's in the file if I want to crawl people who are interested in Selena Gomez, Donal Trump, and Vladimir Putin:
```
instagram
selenagomez
realdonaldtrump
president_vladimir_putin
```

Wait a bit and a folder will be made with crawled profiles as json files.

## Config
Inside `__init__.py`, there is a config dictionary. Each config option is explained in the comments.
Note that `min_collect_media` and `max_collect_media` is trumped if `min_timestamp` is provided as a number.
```
config = {
	'search_algorithm' : 'BFS',                             # Possible values: BFS, DFS
	'profile_path' : './profiles',                          # Path where output data gets saved
	'max_followers' : 10,                                   # How many followers per user to collect
	'max_following' : 15,                                   # how many follows to collect per user
	'min_collect_media' : 10,                               # how many media items to be collected per person. If time is specified, this is ignored
	'max_collect_media' : 10,                               # how many media items to be collected per person. If time is specified, this is ignored
	'max_collect_users' : 1000,                             # how many users to collect in total.
	# 'min_timestamp' : int(time() - 60*60*24*30*2)           # up to how recent you want the posts to be in seconds. If you do not want to use this, put None as value
	'min_timestamp' : None
}
```
