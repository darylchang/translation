from pattern.text.es.inflect import Verbs as SpanishVerbs
from pattern.text.en.inflect import Verbs as EnglishVerbs
from pattern.text.es import find_lemmata
from pattern.text import conjugate

sv = SpanishVerbs()
ev = EnglishVerbs()
tenses = sv.TENSES
tenseMap = {'past':'past', 'infinitive':'infinitive', 'future':'infinitive', 'present':'present'}
moodMap = {None:None, 'indicative':'indicative', 'imperative':'indicative', 'conditional':'indicative', 'subjunctive':'indicative'}
aspectMap = {None:None, 'perfective':'imperfective', 'imperfective':'imperfective', 'progressive':'progressive'}

def fixVerb(elem, verb, tag):
    englishWord = elem[0]
    verb = verb.decode('utf-8')
    base = find_lemmata([[verb, tag]])[0][2]
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
    return (englishWord, elem[1])


def pickCommonTag(wordTag):
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

def fixNouns(candidates, spanishWord, tag):
    return

def fixVerbs(candidates, spanishWord, tag):
    for index, elem in enumerate(candidates):
        candidates[index] = fixVerb(elem, spanishWord, tag)

# Given a list of candidates [(candidate, prior)], update the candidate words
# with verb and noun rules.
def fixWords(candidates, spanishWord, tag, commonTag):
    if(commonTag == 'verb' and tag in [u'MD', u'VBG', u'VB', u'VBN']):
        fixVerbs(candidates, spanishWord, tag)
    elif(commonTag == 'noun'):
        fixNouns(candidates, spanishWord, tag)
    return candidates

# Given a list of mappings from parts of speech to tuples (word, prob), return a list
# of tuples (word, prob), where duplicate words are given their highest probability
# from all parts of speech.
def flattenDict(dict):
    arr = []
    tupleList = [x for senseTup in dict for x in senseTup[1]]
    wordSet = set([tup[0] for tup in tupleList])
    for word in wordSet:
        maxProb = max([tup[1] for tup in tupleList if tup[0]==word])
        arr.append((word, maxProb))
    sumProbs = sum([entry[1] for entry in arr])
    return [(entry[0], entry[1] / sumProbs) for entry in arr]

def getFixedCandidateWords(englishWordDict, spanishWord, tag):
    candidateWords = flattenDict(englishWordDict.items())
    # also: take max of probabilities if same translation in multiple pos
    if tag:
        commonTag = pickCommonTag(tag)
        if commonTag in englishWordDict:
            candidateWords = englishWordDict[commonTag]
            fixWords(candidateWords, spanishWord, tag, commonTag)

    candidateWords.sort(key=lambda x: x[1], reverse=True)
    return candidateWords
