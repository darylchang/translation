# -*- coding: UTF-8 -*-

import math, re
from random import choice

from createDict import createDict

from nltk.model.ngram import NgramModel
from nltk.corpus import brown
from nltk.probability import LidstoneProbDist

from pattern.text.es import tag, find_lemmata
from pattern.text.es.inflect import Verbs as SpanishVerbs
from pattern.text.en.inflect import Verbs as EnglishVerbs
from pattern.text import conjugate

# TODO strategies
# 1: Assign prior probability based on commonality of each translation
# 2: Assign a translation from the POS translation group corresponding to
#		the part of speech of the original word.
# 3: Use POS tags to conjugate the English verb once it's translated.
# TODO:
# 4: Expand verb conjugation by determining person and number of original Spanish verb.
# 5: After running POS tagger, reorder noun-adjectives as adjectives-noun.
# 6: TODO clarify, Use English language model to score potential sentences,
# 		for example, by taking top 3 translations of each word and other changes
# 		and creating a prior probability.
# 7: Try removing common words in the candidate sentences: 'a', 'que', 'en', etc
# 8: Add subjects to Spanish verbs after given conjugation? Part of candidate sentences,
#		evaluate with language model

class Translator:

	# Create and store dictionary of word-to-word translations
	def __init__(self):
		self.translationDict = createDict()
		#est = lambda fdist, bins: LidstoneProbDist(fdist, 0.2)
		# self.ngramModel = NgramModel(3, brown.words(), estimator=est)
		# TODO: store model in its own file?

	# TODO: put sentence in its own object, where each object holds both the original
	# and translated sentence and the sum of the logprobs of the translation model
	# *FOR EACH SPANISH WORD* (so that multiple english words may be produced from
	# single Spanish word).
	def scoreSentence(self, spanishSentence, englishSentence):
		totalScore = 0.0
		for i in range(len(englishSentence)):
			# Calculate the log prob of the trigram
			englishWord = englishSentence[i]
			context = englishSentence[i-2:i]
			logprob = self.ngramModel.logprob(englishWord, context)

			# Calculate the log prob of translating from the English word
			# to the Spanish word
			spanishWord = spanishSentence[i]
			words = self.translationDict[spanishWord].values()[0]
			matches = filter(lambda x:x[0] == englishWord,
									   words)
			translationProb = math.log(filter(lambda x:x[0] == englishWord,
									   words)[0][1]) if matches else None

			print spanishWord, englishWord, translationProb

			totalScore += logprob
			if translationProb:
				totalScore += translationProb
		print totalScore

	# Replace punctuation marks in the final translation based on their
	# positions in the original sentence.
	def addPunctuation(self, translationTokens, punctuation):
		for p in punctuation:
			if p[2] == 'before':
				translationTokens[p[0]] = p[1] + translationTokens[p[0]]
			elif p[2] == 'after':
				translationTokens[p[0]] = translationTokens[p[0]] + p[1]
		newTokens = [t.decode('utf-8') for t in translationTokens]
		return ' '.join(newTokens)

	def pickCommonTag(self, wordTag):
		if wordTag in ['CC']:
			return 'conjunction'
		elif wordTag in ['CD', 'EX', 'FW', 'NN', 'NNS', 'NNP', 'NNPS']:
			return 'noun'
		elif wordTag in ['JJ', 'JJR', 'JJS', 'LS', 'PDT', 'POS', 'WDT']:
			return 'adjective'
		elif wordTag in ['PRP', 'PRP$', 'WP', 'WP$']:
			return 'pronoun'
		elif wordTag in ['RB', 'RBR', 'RBS', 'WRB']:
			return 'adverb'
		elif wordTag in ['RP']:
			return 'particle'
		elif wordTag in ['TO', 'IN']:
			return 'preposition'
		elif wordTag in ['UH']:
			return 'interjection'
		elif wordTag in ['DT']:
			return 'article'
		elif wordTag in ['MD', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']:
			return 'verb'

	# TODO documentation/explanation
	def adjustVerb(self, spanishWord, tag, englishVerb):
		if tag == 'VB':
			return conjugate(englishVerb, 'inf')
		elif tag == 'VBG':
			return conjugate(englishVerb, 'part')
		elif tag == 'VBN':
			return conjugate(englishVerb, 'ppart')
		elif tag == 'VBD':
			return conjugate(englishVerb, 'p')
		elif tag == 'VBP':
			return conjugate(englishVerb, '1sg')
		elif tag == 'VBZ':
			return conjugate(englishVerb, '3sg')
		elif tag == 'MD':
			return englishVerb # return conjugate(englishVerb, tense='PRESENT', negated=False)
		return englishVerb

	def pickEnglishWord(self, spanishWord, pickHighest, wordTag=None):
		englishWordDict = self.translationDict[spanishWord]
		# == Strategy 2 == 
		# Use the part-of-speech tag of the Spanish word
		if wordTag:
			commonTag = self.pickCommonTag(wordTag)
			if commonTag in englishWordDict:
				candidateWords = englishWordDict[commonTag]
			else:
				candidateWords = englishWordDict.items()[0][1]
		else:
			candidateWords = englishWordDict.items()[0][1]
		
		# == Strategy 1 == 
		# For a given Spanish word, pick the English word with the highest
		# translation probability. See createDict for the exponential decay
		# function that assigns translation model priors.
		if pickHighest:
			englishWord = max(candidateWords, key=lambda x:x[1])[0]
		else:
			englishWord = choice(candidateWords)[0]
		
		# == Strategy X == TODO doc
		supportedTags = set(['MD', 'VB', 'VBG', 'VBN', 'VBD', 'VBP', 'VBZ'])
		#print 'Tag of', spanishWord, '=', wordTag
		if wordTag in supportedTags:
			englishAdjusted = self.adjustVerb(spanishWord, wordTag, englishWord)
			#print 'Adjusted', englishWord, 'to:', englishAdjusted
			return englishAdjusted

		return englishWord

	def translate(self, pickHighest=True, tagging=True):
		f = open('corpus_dev.txt')
		sentences = [line.split() for line in f.readlines()]
		punctuationChars = ',.\'\":'

		# Iterate through sentences and create translation for each
		for sentence in sentences:
			translation = []
			punctuation = []
			noPunct = re.sub('[,\.\'\":]','', ' '.join(sentence))
			noPunct = noPunct.decode('utf-8')
			tags = tag(noPunct)

			# ===> TODO: 2 strategies: verb and noun correction
			# get spanish tags (english tags too?), parse tree via:
			# 		taggedSentence = spanishSplit(spanishParse(sentence, tagset='parole'))[0]
			#		for word in taggedSentence (see http://www.clips.ua.ac.be/pages/pattern-es bottom for format):
			# 		if word.tag is some verb tag (see http://www.lsi.upc.edu/~nlp/SVMTool/parole.html):
			#			base = findLemmata(verb, tag)
			#			for tense in Verbs.TENSES:
			#				conjugated = conjugate(base, tense)
			#				if conjugated == word: use english.conjugate(tense)
			#			if no match, use english word
			#		if word.tag is some noun tag:
			#			if spanish noun is pluralized
			#				pluralize translation

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
				if tagging:
					wordTag = tags[index][1]
					englishWord = self.pickEnglishWord(spanishWord, pickHighest, wordTag)
				else:
					englishWord = self.pickEnglishWord(spanishWord, pickHighest)
 
                # === Strategy 3 === 
				# Conjugate English verb based on Spanish verb tense	
				sv = SpanishVerbs()
				ev = EnglishVerbs()
				tenses = sv.TENSES
				tenseMap = {'past':'past', 'infinitive':'infinitive', 'future':'infinitive', 'present':'present'}
				moodMap = {None:None, 'indicative':'indicative', 'imperative':'indicative', 'conditional':'indicative', 'subjunctive':'indicative'}
				aspectMap = {None:None, 'perfective':'imperfective', 'imperfective':'imperfective', 'progressive':'progressive'}
				
				if wordTag in [u'MD', u'VBG', u'VB', u'VBN']:
					verb = tags[index][0]
					base = find_lemmata([[verb, tags[index][1]]])[0][2]
					# Find the tense that will recreate the verb
					for tense in tenses:
						candidateVerb = sv.conjugate(base,          # estar
													tense[0],   # future
													tense[1],   # 1
													tense[2],   # plural
													tense[3],   # indicative
													tense[4])   # imperfective
						if candidateVerb == verb:
							englishTense = (tenseMap[tense[0]], tense[1], 
											tense[2], moodMap[tense[3]],
											aspectMap[tense[4]])
							#print verb, englishWord, englishTense
							englishWord = ev.conjugate(englishWord, 
											   englishTense[0],
											   englishTense[1],
											   englishTense[2],
											   englishTense[3],
											   englishTense[4])	
							if tense[0] == 'future':
								englishWord = 'will ' + englishWord
							elif englishTense[0] == 'infinitive':
								englishWord = 'to ' + englishWord

				translation.append(englishWord)
			
			# Format result and print
			translation[0] = translation[0].capitalize() # Capitalize first word
			translation = self.addPunctuation(translation, punctuation)
			print ' '.join(sentence), '\n', translation, '\n\n'


	def translateBaseline(self):
		f = open('corpus_dev.txt')
		sentences = [line.split() for line in f.readlines()]
		punctuationChars = ',.\'\":'

		for sentence in sentences:
			translation = []
			noPunct = re.sub('[,\.\'\":]','', ' '.join(sentence))
			noPunct = noPunct.decode('utf-8')
		
			for index, token in enumerate(sentence):
				# Remove punctuation
				spanishWord = re.sub('[,\.\'\":]','', token).lower()

				# Select English word translation based on translation model
				englishWord = self.pickEnglishWord(spanishWord, False)
				translation.append(englishWord)

			print ' '.join(sentence), '\n', ' '.join(translation), '\n\n'

# Run cs124_translate
if __name__=="__main__":
	t = Translator()
	#t.translate(pickHighest=True, tagging=True)
	t.translateBaseline()


