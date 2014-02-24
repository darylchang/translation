import re
from createDict import createDict
from random import choice
from pattern.text.es.__init__ import tag

class Translator:

	# Create and store dictionary of word-to-word translations
	def __init__(self):
		self.translationDict = createDict()

	# Replace punctuation marks in the final translation based on their
	# positions in the original sentence.
	def addPunctuation(self, translationTokens, punctuation):
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

	def toEnglishWord(self, spanishWord, sentence, pickHighest=True, tagging=True):
		englishWordDict = self.translationDict[spanishWord]
		candidateWords = englishWordDict.items()[0][1]
		
		# == Strategy 1 == 
		# For a given Spanish word, pick the English word with the highest
		# translation probability. 
		if pickHighest:
			englishWord = max(candidateWords, key=lambda x:x[1])[0]
		else:
			englishWord = choice(candidateWords)[0]
		return englishWord

	def translate(self):
		f = open('corpus_dev.txt')
		sentences = [line.split() for line in f.readlines()]
		punctuationChars = ',.\'\":'

		# Iterate through sentences and create translation for each
		for sentence in sentences:
			translation = []
			punctuation = []

			# Iterate through tokens in sentence
			for index, token in enumerate(sentence): # TODO: function to tokenize in phrases?
				# Record punctuation at start and end for later recovery
				if token[0] in punctuationChars:
					punctuation.append((index, token[0], 'before'))
				if token[-1] in punctuationChars:
					punctuation.append((index, token[-1], 'after'))

				# Remove punctuation
				spanishWord = re.sub('[,\.\'\":]','', token).lower()

				# Select English word translation based on translation model
				englishWord = self.toEnglishWord(spanishWord, sentence)
				translation.append(englishWord)
			
			# Format result and print
			translation[0] = translation[0].capitalize() # Capitalize first word
			translation = self.addPunctuation(translation, punctuation)
			print ' '.join(sentence), '\n', translation, '\n\n'

# Run cs124_translate
if __name__=="__main__":
	t = Translator()
	t.translate()


