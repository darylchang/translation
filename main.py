import re
from createTranslations import createTranslations
from random import choice

def baseline():
	f = open('corpus_dev.txt')
	sentences = [line.split() for line in f.readlines()]
	translationDict = createTranslations()
	#print sorted(translationDict.keys())
	for sentence in sentences:
		translation = []
		for token in sentence:
			spanishWord = re.sub('[,\.\'\":]','', token).lower()
			englishWordArr = translationDict[spanishWord]
			englishWord = choice(englishWordArr)[1]
			translation.append(englishWord)
		print ' '.join(sentence), '\n', ' '.join(translation)
		print '\n'
			#print spanishWord, englishWord
			#i = re.finditer("[,\.\'\":]", token)
			#indices = [m.start(0) for m in i]


baseline()
