import math

class Sentence:

    # Create a sentence with two things:
    # 1. A list of English tokens (may be multiple words). For example:
    #   ['The', 'cat', 'went to', 'the', 'city park']
    # 2. A list of the prior probabilities (via the translation model) for each token. For example:
    #   [0.25, 0.5, 0.83333, 0.1]
    def __init__(self, tokensList, probabilities, translationModel=None):
        self.tokens = [word for token in tokensList for word in token.split(' ')]
        self.phraseTokens = tokensList
        self.priorLogProb = self.getLogProb(probabilities)
        self.priorWeight = 0.8 # TODO: adjust up/down as needed
        self.model = translationModel

    def getLogProb(self, probabilities):
        sum = 0.0
        for prob in probabilities:
            sum += math.log(prob)
        return sum

    def score(self):
        priorScore = self.priorWeight * (self.priorLogProb)
        langModelScore = 0.0

        if self.model:
            for i in range(len(self.tokens)):
                englishWord = self.tokens[i]
                context = self.tokens[i-2:i]
                langModelScore -= self.model.logprob(englishWord, context)

        langModelScore /= len(self.tokens) * 2 # Normalize by length of list
        langModelScore *= (1.0 - self.priorWeight)
        totalScore = priorScore + langModelScore
        #print 'Returning total score =', totalScore, 'from components langModel =', langModelScore, 'priorModel =', priorScore
        return totalScore
