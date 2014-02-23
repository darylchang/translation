import re
from createTranslations import createTranslations
from random import choice

# === Strategy 1 ===
# Give prior probabilities to each translation based on the translation
# model, i.e., the order in which they are most often translated from the
# spanish word. Modeled using exponential decay function.
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

# === Strategy 2 ===
# Replace punctuation marks in the final translation based on their
# positions in the original sentence.
def addPunctuation(translationTokens, punctuation):
	for p in punctuation:
		if p[2] == 'before':
			translationTokens[p[0]] = p[1] + translationTokens[p[0]]
		elif p[2] == 'after':
			translationTokens[p[0]] = translationTokens[p[0]] + p[1]
	return ' '.join(translationTokens)


# TODO strategies
# - (BIG) Run Spanish POS tagger, select translations with correct POS
#		- make sure all dictionary translations are ordered by "goodness"
# - (BIG) After running POS tagger, reorder noun-adjectives as adjectives-noun
# - (BIG PROBLEM) Fix verb form; need conjugations.
#		Put all verb forms in dictionary? Or use Spanish conjugation tool?
#		If infinitive, replace with phrase "to [definition]"
# - (BIG) Introduce English language model to improve translations
#		Introduce randomness in picking words, score sentences/n-grams, pick best
# - ?


def pickWord(translations):
	"Return the (word, probability) pair with the highest probability"
	return max(translations, key = lambda x:x[1])

def cs124_translate():
	f = open('corpus_dev.txt')
	sentences = [line.split() for line in f.readlines()]
	translationDict = createTranslations()
	punctuationChars = ',.\'\":'
	#print sorted(translationDict.keys())
	for sentence in sentences:
		translation = []
		punctuation = []
		for index, token in enumerate(sentence): # TODO: function to tokenize in phrases?
			if token[0] in punctuationChars:
				punctuation.append((index, token[0], 'before'))
			if token[len(token)-1] in punctuationChars:
				punctuation.append((index, token[len(token)-1], 'after'))
			spanishWord = re.sub('[,\.\'\":]','', token).lower()	
			englishWordArr = translationDict[spanishWord]
			priors = getPriors([pair[1] for pair in englishWordArr])
			englishWord = pickWord(priors)[0]
			translation.append(englishWord)
		
		translation[0] = translation[0].capitalize() # Capitalize first word
		translation = addPunctuation(translation, punctuation)
		print ' '.join(sentence), '\n', translation
		print '\n'
			#print spanishWord, englishWord
			#i = re.finditer("[,\.\'\":]", token)
			#indices = [m.start(0) for m in i]

cs124_translate()


