import re

def createDict():
	f = open('dictionary.txt', 'r').readlines()
	translationDict = {}
	for line in f:
		spaceIndex = line.find(' ')
		word = line[:spaceIndex] 
		translations = line[spaceIndex+1:]

		if not re.search('\[(.*?)\]', translations):
			# Takes care of proper nouns
			translationDict[word] = {'noun' : [(word.capitalize(), 1.0)]}
		else:
			# Parse word translations
			posGroups = re.findall('\[(.*?)\]', translations)
			posGroups = [posGroup.split(':') for posGroup in posGroups]  # 'noun:boat,car' => ['noun', 'boat,car']
			posGroups = [(posGroup[0], posGroup[1].split(',')) for posGroup in posGroups]  # ('noun', ['boat', 'car'])
			wordDict = dict(posGroups)

			# Add prior translation probability to each word using exponential decay model
			for pos, translationWords in wordDict.items():
				newTranslationWords = []
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
					newTranslationWords.append((translationWords[i], thisProbMass))

				wordDict[pos] = newTranslationWords
			translationDict[word] = wordDict

	return translationDict

# createDict()
