from random import sample, shuffle

def randselect(list, num):
	l = len(list)
	if l <= num:
		return shuffle(list)
	if l > 5*num: 
		return sample(list[:5*num], num)

def byteify(input):
	if isinstance(input, dict):
		return {byteify(key): byteify(value)
				for key, value in input.iteritems()}
	elif isinstance(input, list):
		return [byteify(element) for element in input]
	elif isinstance(input, unicode):
		return input.encode('utf-8')
	else:
		return input

