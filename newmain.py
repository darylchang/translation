# -*- coding: UTF-8 -*-

# Python library
import math, re
from random import choice

# Our files
from createDict import createDict
from fixWords import getFixedCandidateWords
from sentence import Sentence

# NLP Modules
from nltk.model.ngram import NgramModel
from nltk.corpus import brown
from nltk.probability import LidstoneProbDist
from pattern.text.es import tag

class Translator:

    # Create and store dictionary of word-to-word translations
    def __init__(self):
        self.translationDict = createDict()
        est = lambda fdist, bins: LidstoneProbDist(fdist, 0.2)
        self.ngramModel = NgramModel(3, brown.words(), estimator=est)
        # TODO: store model in its own file?

    def getSentences(self, spanishSentence, candidateslist):
        sentences = []

        # TODO: generate many candidate sentences. The trivial case (take first word
        # from every candidate) is shown here.
        
        tokens = [candidate[0][0] for candidate in candidatesList]
        probs = [candidate[0][1] for candidate in candidatesList]
        sentence = Sentence(tokens, probs, self.ngramModel)
        sentences.append(sentence)

        return sentences

    def getBestTranslation(self, spanishSentence, candidatesList):
        sentences = getSentences(spanishSentence, candidatesList)
        sentenceScores = [sentence.score for sentence in sentences]
        return sentences[sentenceScores.index(max(sentenceScores))]

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

    def translate(self, pickHighest=True, tagging=True):
        # TODO: configure turning off various parts? or reimplement baseline
        f = open('corpus_dev.txt')
        sentences = [line.split() for line in f.readlines()]
        punctuationChars = ',.\'\":'

        # Iterate through sentences and create translation for each
        for sentence in sentences:
            punctuation = []
            
            # Do part-of-speech tagging
            noPunct = re.sub('[,\.\'\":]','', ' '.join(sentence))
            noPunct = noPunct.decode('utf-8')
            tags = tag(noPunct)

            # For each token in the Spanish sentence, store a list of candidates
            # in this outer list. Each candidate is a (translation, probability)
            # pair, where translation is an English word (perhaps adjusted for
            # tense, plurality, etc) and probability is the prior probability
            # based on the translation model.
            candidatesList = []

            # Iterate through tokens in sentence
            # TODO: possible strategy: tokenize in phrases
            for index, token in enumerate(sentence):

                # Record punctuation at start and end for later recovery
                if token[0] in punctuationChars:
                    punctuation.append((index, token[0], 'before'))
                if token[-1] in punctuationChars:
                    punctuation.append((index, token[-1], 'after'))
                spanishWord = re.sub('[,\.\'\":]','', token).lower()
                
                # Generate candidate translations for this token
                wordTag = tags[index][1]
                englishWordDict = self.translationDict[spanishWord]
                candidates = getFixedCandidateWords(englishWordDict, spanishWord, wordTag)
                candidatesList.append(candidates)
            
            # Given the candidates list, do post-processing to select a best
            # English sentence translation.
            translation = getBestTranslation(sentence, candidatesList)

            # Format result and print
            translation = ' '.join(translation)
            translation[0] = translation[0].capitalize() # Capitalize first word
            translation = self.addPunctuation(translation, punctuation)
            print ' '.join(sentence), '\n', translation, '\n\n'

# Run cs124_translate
if __name__=="__main__":
    t = Translator()
    t.translate(pickHighest=True, tagging=True)



# TODO writeup strategies
# 1: Assign prior probability based on commonality of each translation
# 2: Assign a translation from the POS translation group corresponding to
#       the part of speech of the original word.
# 3: Use POS tags to conjugate the English verb once it's translated.
# TODO:
# 4: Expand verb conjugation by determining person and number of original Spanish verb.
# 5: After running POS tagger, reorder noun-adjectives as adjectives-noun.
# 6: TODO clarify, Use English language model to score potential sentences,
#       for example, by taking top 3 translations of each word and other changes
#       and creating a prior probability.
# 7: Try removing common words in the candidate sentences: 'a', 'que', 'en', etc
# 8: Add subjects to Spanish verbs after given conjugation? Part of candidate sentences,
#       evaluate with language model