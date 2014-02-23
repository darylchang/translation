import re

def baseline():
	f = open('corpus_dev.txt')
	sentences = [line.split() for line in f.readlines()]
	for sentence in sentences:
		translation = []
		for token in sentence:
			spanishWord = re.sub('[,\.\'\":]','', token)
			englishWord = translations[spanishWord]
			#i = re.finditer("[,\.\'\":]", token)
			#indices = [m.start(0) for m in i]


baseline()
