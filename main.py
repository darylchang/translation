import re
from createTranslations import createTranslations
from random import choice

def getPriors(translationWords):
	priorPairs = []
	probMass = 1.0
	lastIndex = len(translationWords) - 1
	for i in range(0, lastIndex + 1):
		thisProbMass = probMass;
		if i < (lastIndex - 1):
			probMass /= 2.0
			thisProbMass = probMass
		elif i == lastIndex - 1:
			thisProbMass = 2.0 * probMass / 3.0
			probMass /= 3.0
		priorPairs.append((translationWords[i], thisProbMass))
	return priorPairs

def pickWord(translations):
	"Return the (word, probability) pair with the highest probability"
	return max(translations, key = lambda x:x[1])

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
			priors = getPriors([pair[1] for pair in englishWordArr])
			#englishWord = choice(englishWordArr)[1]
			englishWord = pickWord(priors)[0]
			translation.append(englishWord)		
		translation = (' '.join(translation)).capitalize()
		print ' '.join(sentence), '\n', translation
		print '\n'
			#print spanishWord, englishWord
			#i = re.finditer("[,\.\'\":]", token)
			#indices = [m.start(0) for m in i]

baseline()


