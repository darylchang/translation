# -*- coding: UTF-8 -*-

# Python library
import copy, math, re
from random import choice, random

# Our files
from createDict import createDict
from fixWords import getFixedCandidateWords, pickCommonTag
from sentence import Sentence
from translationUtils import iterBools

# NLP Modules
from nltk.model.ngram import NgramModel
from nltk.corpus import brown, reuters
from nltk.probability import LidstoneProbDist
from pattern.text.es import tag

class Translator:

    # Create and store dictionary of word-to-word translations
    def __init__(self):
        self.translationDict = createDict()
        self.words_to_remove = ['of', 'the', 'what', 'in', 'for', 'about', 'that', 'when', 'than', 'by', 'so']
        self.words_to_add = ['a', 'the']
        est = lambda fdist, bins: LidstoneProbDist(fdist, 0.2)
        # with open('ngramModel.pickle','r') as handle:
        #     self.ngramModel = dill.load(handle)
        words = reuters.words() + brown.words()
        self.ngramModel = NgramModel(3, words, estimator=est)
        self.beamSize = 6
        # TODO: store model in its own file?

    # STRATEGIES FOR GETTING SENTENCES
    #   1. Probabilistic or pruning (beam) search
    #   2. Reordering (nouns/adjectives, etc)
    #   3. Adding subject before verbs
    #   4. Removing/adding smaller words ('a/the' before noun, remove duplicate words, etc)
    #   5. Flip verb and negation (not was -> was not)
    
    def chooseWord(self, candidates):
        randDec = random()
        upto = 0.0
        for candidate in candidates:
            upto += candidate[1]
            if(upto > randDec):
                return candidate[0], candidate[1]
        return candidates[0][0], candidates[0][1]

    def generateSentences(self, candidatesList, confidenceValue=1.0, removedTokenIndices=[], num=100000):
        sentences = []
        for i in range(1, num+1):
            tokens = []
            probs = []
            for candidates in candidatesList:
                token, prob = self.chooseWord(candidates)
                tokens.append(token)
                probs.append(prob)
            sentences.append(Sentence(tokens, probs, confidenceValue, removedTokenIndices, self.ngramModel))
        return sentences

    # Post-translation processing to generate better sentences

    def hasStopWord(self, subCandidatesList):
        eligibleWords = []
        for tup in subCandidatesList:
            eligibleWords.extend(tup[0].split(' '))
        return [stop_word for stop_word in self.words_to_remove if stop_word in eligibleWords]

    def shouldRemoveWord(self, candidatesList, index):
        sublist = candidatesList[index]
        if not self.hasStopWord(candidatesList[index]):
            return False

        # Keep vital stop-word phrases like "in the", "of the", etc together
        saveWords = ['of', 'in', 'at', 'for', 'to']
        for candidate in candidatesList[index]:
            tokens = candidate[0].split(' ')
            if len(tokens) > 1 and tokens[-1] == 'the':
                return False
            if tokens[0] == 'the' and index > 0:
                for prevCandidate in candidatesList[index-1]:
                    if prevCandidate[0] in saveWords:
                        return False
            if tokens[0] in saveWords and index < len(candidatesList) - 1:
                for nextCandidate in candidatesList[index+1]:
                    if nextCandidate[0] == 'the':
                        return False

        if index > 0 and self.hasStopWord(candidatesList[index-1]):
            return True
        if (index < len(candidatesList) - 1) and self.hasStopWord(candidatesList[index+1]):
            return True
        return False

    # Get candidate sentences with certain common null words in Spanish->English
    # translations removed.
    def getRemovedSentences(self, candidatesList):
        sentences = []

        remove_positions = [i for i in range(0, len(candidatesList)) if self.shouldRemoveWord(candidatesList, i)]
        remove_arrs = iterBools([], remove_positions, 0, len(remove_positions))
        for remove_arr in remove_arrs:
            newCandidatesList = []
            removedTokenIndices = []
            removed = 0
            for index, candidatesSublist in enumerate(candidatesList):
                remove = index in remove_positions and remove_arr[remove_positions.index(index)]
                if remove:
                    removed += 1
                    removedTokenIndices.append(index)
                else:
                    newCandidatesList.append(candidatesSublist)
            confidence = 1.0 - (0.025 * removed)
            #print 'Removed', removed, 'stop words for a confidence value of:',confidence
            if removed > 0:
                sentences.extend(self.generateSentences(newCandidatesList, confidence, removedTokenIndices, 2500))
        print 'Returning', len(sentences), 'with removed stop words'
        return sentences

    # Any special post-processing steps
    def getPermutedSentences(self, candidatesList, tagList):
        sentences = []
        sentences.extend(self.getRemovedSentences(candidatesList))
        return sentences

    def getSentences(self, spanishSentence, candidatesList, tagList):
        sentences = []
        sentences.extend(self.generateSentences(candidatesList))
        sentences.extend(self.getPermutedSentences(candidatesList, tagList))
        return sentences

    def getBestTranslation(self, spanishSentence, candidatesList, tagList, beamSearch=False):
        if beamSearch:
            sentences = [([],0.) for i in xrange(self.beamSize)]
            for i in range(len(spanishSentence)):
                candidateSentences = []
                candidateWords = candidatesList[i]
                for sentence, prob in sentences:
                    for candidateWord, candidateProb in candidateWords:
                        newSentence = sentence + [candidateWord]
                        context = sentence[-2:]

                        # Calculate new probability based on reciprocal negative probabilities
                        rCandidateProb = -1./math.log(candidateProb) if candidateProb != 1. else 0.
                        if self.ngramModel.prob(candidateWord, context) < 1.:
                            rLangProb = -1./(math.log(self.ngramModel.prob(candidateWord, context)))
                        else:
                            rLangProb = 10.
                        #print 'Candidate word: ', candidateWord, 'Translation prob is: ', rCandidateProb, 'Language prob: ', rLangProb
                        newProb = prob + rCandidateProb + rLangProb

                        candidateSentences.append((newSentence, newProb))
                candidateSentences.sort(key=lambda x:x[1], reverse=True)
                
                # Eliminate duplicates
                temp = []
                for candidateSentence in candidateSentences:
                    if candidateSentence not in temp:
                        temp.append(candidateSentence)
                candidateSentences = temp

                sentences = candidateSentences[:self.beamSize]
                #print sentences, '\n'

            bestSentence = max(sentences, key=lambda x:x[1])
            return bestSentence[0], []
        else:
            sentences = self.getSentences(spanishSentence, candidatesList, tagList)
            sentenceTups = [(sentence, sentence.score()) for sentence in sentences]
            bestSentence = max(sentenceTups, key=lambda x:x[1])[0]
            return bestSentence.phraseTokens, bestSentence.removedTokenIndices

    # Adjust punctuation indices down based on the removed indices of phrases.
    def adjustPunctuationIndices(self, punctuation, removedIndices):
        removedIndices.sort
        punctuationFixed = []
        for p in punctuation:
            p = list(p)
            preceding = len([i for i in removedIndices if i < p[0]])
            if p[0] in removedIndices:
                p[0] = p[0] - preceding - 1
            else:
                p[0] = p[0] - preceding
            if p[0] >= 0:
                punctuationFixed.append(tuple(p))
        return punctuationFixed

    # Replace punctuation marks in the final translation based on their
    # positions in the original sentence.
    def addPunctuation(self, phraseTokens, removedIndices, punctuation):
        punctuation = self.adjustPunctuationIndices(punctuation, removedIndices)
        for p in punctuation:
            if p[2] == 'before':
                phraseTokens[p[0]] = p[1] + phraseTokens[p[0]]
            elif p[2] == 'after':
                phraseTokens[p[0]] = phraseTokens[p[0]] + p[1]
        newTokens = [t.decode('utf-8') for t in phraseTokens]
        return newTokens

    def removeDuplicates(self, translation):
        translation = translation.split()
        newTranslation = []
        i = 0
        while i < len(translation) - 1:
            newTranslation.append(translation[i])
            while translation[i] == translation[i+1]:
                i += 1
            i += 1
        newTranslation.append(translation[i])

        return ' '.join(newTranslation)
        
    def processSentence(self, rawSentence, tags):
        wordsToRemove = ['a', 'le', 'se']
        sentence = copy.deepcopy(rawSentence)
        sentence = [word.lower() for word in sentence]
        for word in wordsToRemove:
            while word in sentence:
                i = sentence.index(word)
                sentence.pop(i)
                tags.pop(i)

        # # Words after determiners must be nouns
        # indices = [i for i,x in enumerate(sentence) if x in ['el', 'la', 'los', 'las']]
        # for i in indices:
        #     if tags[i+1][1] not in ['NN', 'NNS', 'NNP', 'NNPS']:
        #         tags[i+1] = (tags[i+1][0], 'NN')

        # Remove any 'de' that follows a preposition and 
        # label all 'de's as prepositions
        indices = [i for i,x in enumerate(sentence) if x=='de' or x=='del']
        removed = 0
        for i in indices:
            tags[i-removed] = (tags[i-removed][0], 'IN')
            if tags[i-1-removed][1] == u'IN':
                sentence.pop(i-removed)
                tags.pop(i-removed)
                removed += 1

        # Replace any 'al' that follows a verb with 'el'
        indices = [i for i,x in enumerate(sentence) if x=='al']
        for i in indices:
            if tags[i-1][1] in ['MD', 'VB', 'VBD', 'VBG', 'VBP', 'VBZ']:
                sentence[i] = 'el'
                tags[i] = ('el', 'DT')

        # Add a determiner in front of nouns that follow prepositions
        # indices = [i for i,x in enumerate(tags) if x[1] in ['NN', 'NNS']]
        # added = 0
        # for i in indices:
        #     adjustedIndex = i + added
        #     if tags[adjustedIndex-1][1] == 'IN':
        #         added += 1
        #         sentence = sentence[:adjustedIndex] + ['el'] + sentence[adjustedIndex:]
        #         tags = tags[:adjustedIndex] + [('el', 'DT')] + tags[adjustedIndex:]

        # Flip adjectives and nouns
        indices = [i for i,x in enumerate(tags) if x[1]=='JJ']
        for i in indices:
            if i-1>0 and tags[i-1][1] in ['NN', 'NNS']:
                punctuationChars = ',.\'\":' 
                rawNoun, rawAdj = sentence[i-1], sentence[i]

                # Swap punctuation
                if rawNoun[0] in punctuationChars:
                    adj = rawNoun[0] + rawAdj
                    noun = rawNoun[1:]
                elif rawNoun[-1] in punctuationChars:
                    adj = rawAdj + rawNoun[-1]
                    noun = rawNoun[:-1]
                elif rawAdj[0] in punctuationChars:
                    noun = rawAdj[0] + rawNoun
                    adj = rawAdj[1:]
                elif rawAdj[-1] in punctuationChars:
                    noun = rawNoun + rawAdj[-1]
                    adj = rawAdj[:-1]
                else:
                    adj = rawAdj
                    noun = rawNoun

                sentence[i-1] = adj
                sentence[i] = noun

                tempTag = tags[i]
                tags[i-1] = tags[i]
                tags[i] = tempTag

        # Flip verbs and negation ('no era' -> 'era no')
        indices = [i for i,x in enumerate(sentence) if x=='no']
        for i in indices:
            if i+1<len(tags) and tags[i+1][1] in ['VB', 'VBD', 'VBG', 'VBP', 'VBZ']:
                verbTag = tags[i+1]
                verb = sentence[i+1]

                sentence[i+1] = sentence[i]
                tags[i+1] = tags[i]
                sentence[i] = verb
                tags[i] = verbTag
        #print tags
        return sentence, tags

    def translate(self, pickHighest=True, tagging=True):
        # TODO: configure turning off various parts? or reimplement baseline
        f = open('corpus_dev.txt')
        rawSentences = [line.split() for line in f.readlines()]
        punctuationChars = ',.\'\":'    

        # Iterate through sentences and create translation for each
        for rawSentence in rawSentences:
            punctuation = []
            
            # Do part-of-speech tagging
            noPunct = re.sub('[,\.\'\":]','', ' '.join(rawSentence))
            noPunct = noPunct.decode('utf-8')
            tags = tag(noPunct)

            # Remove words
            sentence, tags = self.processSentence(rawSentence, tags)

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
                if len(token) > 1 and token[-2] in punctuationChars:
                    punctuation.append((index, token[-2], 'after'))
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
            phraseTokens, removedIndices = self.getBestTranslation(sentence, candidatesList, tags)

            # Format result and print
            translationTokens = self.addPunctuation(phraseTokens, removedIndices, punctuation)
            #translationTokens = [token.decode('utf-8') for token in translationTokens]
            translation = ' '.join(translationTokens)
            translation = self.removeDuplicates(translation)
            translation = translation[0].capitalize() + translation[1:] # Capitalize first word
            #sentence = [token.encode('utf-8') for token in sentence]
            # print sentence
            # print u" ".join(sentence)
            joinedSentence = " ".join(rawSentence)
            print joinedSentence, '\n', translation, '\n\n'

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